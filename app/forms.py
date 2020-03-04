from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

class MyAuthForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Usuario'})
    self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Contraseña'})


class MyPasswordChangeForm(PasswordChangeForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.base_fields['old_password'].widget.attrs['class'] = 'form-control'
    self.base_fields['new_password1'].widget.attrs['class'] = 'form-control'
    self.base_fields['new_password2'].widget.attrs['class'] = 'form-control'