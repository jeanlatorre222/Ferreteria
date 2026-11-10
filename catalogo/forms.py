from django import forms


class PerfilDatosForm(forms.Form):
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
    )
