from django import forms
from .models import BienesAsignados

class BienesAsignadosForm(forms.ModelForm):
    class Meta:
        model = BienesAsignados
        fields = ['trabajo', 'bien', 'cantidad_usada', 'unidades_asignadas']

    def clean(self):
        cleaned_data = super().clean()
        bien = cleaned_data.get('bien')
        cantidad_usada = cleaned_data.get('cantidad_usada')
        unidades_asignadas = cleaned_data.get('unidades_asignadas')

        if bien:
            if bien.requiere_identificador:
                if not unidades_asignadas:
                    raise forms.ValidationError("Debes asignar al menos una unidad.")
                cleaned_data['cantidad_usada'] = unidades_asignadas.count()
            else:
                if not cantidad_usada:
                    raise forms.ValidationError("Debes indicar la cantidad usada.")
                if unidades_asignadas:
                    raise forms.ValidationError("No debes seleccionar unidades si el bien no lo requiere.")
        
        return cleaned_data