from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import UserAccount
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse


class CustomInputWidget(forms.TextInput):
    def __init__(self, icon_class, placeholder, input_type='text', maxlength=None, autocomplete=None, *args, **kwargs):
        self.icon_class = icon_class
        self.placeholder = placeholder
        self.input_type = input_type
        self.maxlength = maxlength
        self.autocomplete = autocomplete
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        attrs.update({
            'type': self.input_type,
            'placeholder': self.placeholder,
            'required': True,
            'name': name,
        })
        
        if self.maxlength:
            attrs['maxlength'] = self.maxlength
        if self.autocomplete:
            attrs['autocomplete'] = self.autocomplete
        
        input_html = super().render(name, value, attrs, renderer)
        
        return format_html(
            '<div class="input-group">'
            '<div class="input-container">'
            '<i class="{} input-icon"></i>'
            '{}'
            '</div>'
            '</div>',
            self.icon_class,
            input_html
        )

class CustomPasswordWidget(forms.PasswordInput):
    def __init__(self, placeholder, maxlength=None, *args, **kwargs):
        self.placeholder = placeholder
        self.maxlength = maxlength
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        attrs.update({
            'type': 'password',
            'placeholder': self.placeholder,
            'required': True,
            'name': name,
            'autocomplete': 'new-password',
        })
        
        if self.maxlength:
            attrs['maxlength'] = self.maxlength
        
        input_html = super().render(name, value, attrs, renderer)
        
        return format_html(
            '<div class="input-group">'
            '<div class="input-container">'
            '<i class="fas fa-lock input-icon"></i>'
            '{}'
            '<button type="button" class="toggle-visibility">'
            '<i class="fas fa-eye-slash"></i>'
            '</button>'
            '</div>'
            '</div>',
            input_html
        )

class CustomNameWidget(forms.TextInput):
    def __init__(self, placeholder, field_name, *args, **kwargs):
        self.placeholder = placeholder
        self.field_name = field_name
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        attrs.update({
            'type': 'text',
            'placeholder': self.placeholder,
            'required': True,
            'maxlength': 30,
            'name': self.field_name,
            'autocomplete': 'given-name' if 'first' in self.field_name.lower() else 'family-name',
        })
        
        input_html = super().render(name, value, attrs, renderer)
        
        return format_html(
            '<div class="input-container">'
            '<i class="fas fa-user input-icon"></i>'
            '{}'
            '</div>',
            input_html
        )

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='',
        widget=CustomPasswordWidget(placeholder='Enter your password', maxlength=19)
    )
    password2 = forms.CharField(
        label='',
        widget=CustomPasswordWidget(placeholder='Confirm password', maxlength=20)
    )

    class Meta:
        model = UserAccount
        fields = ('email', 'username', 'first_name', 'last_name', 'pfp')
        widgets = {
            'email': CustomInputWidget(
                icon_class='fas fa-envelope',
                placeholder='Enter your email address',
                input_type='email',
                maxlength=40,
                autocomplete='email'
            ),
            'username': CustomInputWidget(
                icon_class='fas fa-user',
                placeholder='Username',
                maxlength=30,
                autocomplete='username'
            ),
            'first_name': CustomNameWidget(
                placeholder='First Name',
                field_name='firstName'
            ),
            'last_name': CustomNameWidget(
                placeholder='Last Name',
                field_name='lastName'
            ),
            'pfp': forms.FileInput(attrs={'style': 'display: none;'})  # Hide file input or customize as needed
        }
        labels = {
            'email': '',
            'username': '',
            'first_name': '',
            'last_name': '',
            'pfp': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group first_name and last_name in a single div
        self.fields['first_name'].widget = CustomNameWidget(placeholder='First Name', field_name='firstName')
        self.fields['last_name'].widget = CustomNameWidget(placeholder='Last Name', field_name='lastName')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def as_custom(self):
        """Custom rendering method to handle the name group specially"""
        output = []
        
        # Email field
        output.append(str(self['email']))
        output.append(str(self['username']))
        
        # Name group (first_name and last_name together)
        output.append(
            '<div class="input-group name-group">'
            + str(self['first_name'])
            + str(self['last_name'])
            + '</div>'
        )
        
        # Password fields
        output.append(str(self['password1']))
        output.append(str(self['password2']))
        
        # Form actions
        output.append(
            '<div class="form-actions">'
            '<button type="submit" class="btn btn-primary">'
            'Next <i class="fas fa-angle-right"></i>'
            '</button>'
            '</div>'
        )
        
        # Divider and Google signin
        output.append(
            '<p class="form-switch">'
                'Already have an account?'
                f'<a class="link-btn" href="{reverse("connexion")}"> Login here </a>'
            '</p>'
        )
        
        return mark_safe(''.join(output))

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
