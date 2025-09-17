from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import transaction

from .models import Persona, Correo, Telefono, Direccion
from .forms import (
    PersonaFormulario,
    CorreoFormsetCrear, CorreoFormsetEditar,
    TelefonoFormsetCrear, TelefonoFormsetEditar,
    DireccionFormsetCrear, DireccionFormsetEditar,
)

def personas_listado(request):
    personas = Persona.objects.all()
    return render(request, 'crud_personas/personas_listado.html', {'personas': personas})

def _contexto_formularios(persona=None):
    if persona:
        f_corr_cls = CorreoFormsetEditar if persona.correos.exists() else CorreoFormsetCrear
        f_tel_cls  = TelefonoFormsetEditar if persona.telefonos.exists() else TelefonoFormsetCrear
        f_dir_cls  = DireccionFormsetEditar if persona.direcciones.exists() else DireccionFormsetCrear
        return (
            PersonaFormulario(instance=persona),
            f_corr_cls(instance=persona, prefix='correos'),
            f_tel_cls(instance=persona,  prefix='telefonos'),
            f_dir_cls(instance=persona,  prefix='direcciones'),
        )
    return (
        PersonaFormulario(),
        CorreoFormsetCrear(prefix='correos'),
        TelefonoFormsetCrear(prefix='telefonos'),
        DireccionFormsetCrear(prefix='direcciones'),
    )

# -------- helpers para contar activos del POST (ignorando DELETE) --------

def _correos_activos(formset):
    activos = []
    for f in formset.forms:
        if not hasattr(f, 'cleaned_data'):
            continue
        cd = f.cleaned_data
        if cd.get('DELETE'):
            continue
        correo = (cd.get('correo') or '').strip()
        if correo:
            activos.append(correo)
    return activos

def _telefonos_activos(formset):
    activos = []
    for f in formset.forms:
        if not hasattr(f, 'cleaned_data'):
            continue
        cd = f.cleaned_data
        if cd.get('DELETE'):
            continue
        numero = (cd.get('numero') or '').strip()
        etiqueta = (cd.get('etiqueta') or '').strip()
        if numero:
            activos.append((etiqueta, numero))
    return activos

def _direcciones_activas(formset):
    activos = []
    for f in formset.forms:
        if not hasattr(f, 'cleaned_data'):
            continue
        cd = f.cleaned_data
        if cd.get('DELETE'):
            continue
        linea1 = (cd.get('linea1') or '').strip()
        if linea1:
            activos.append({
                'linea1': linea1,
                'linea2': (cd.get('linea2') or '').strip(),
                'ciudad': (cd.get('ciudad') or '').strip(),
                'estado': (cd.get('estado') or '').strip(),
                'cp': (cd.get('cp') or '').strip(),
                'pais': (cd.get('pais') or '').strip(),
            })
    return activos

def _poner_error_minimo(formset, msg):
    # agrega non_form_error al formset
    formset._non_form_errors = formset.error_class([msg])

@transaction.atomic
def modal_persona_crear(request):
    if request.method == 'GET':
        formulario, f_corr, f_tel, f_dir = _contexto_formularios(None)
        html = render_to_string('crud_personas/_form_persona.html', {
            'titulo_modal': 'Nuevo contacto',
            'formulario': formulario,
            'formset_correos': f_corr,
            'formset_telefonos': f_tel,
            'formset_direcciones': f_dir,
            'url_accion': request.path,
            'modo': 'crear',
        }, request=request)
        return JsonResponse({'ok': True, 'html': html})

    formulario = PersonaFormulario(request.POST, request.FILES)
    f_corr = CorreoFormsetCrear(request.POST, prefix='correos')
    f_tel  = TelefonoFormsetCrear(request.POST, prefix='telefonos')
    f_dir  = DireccionFormsetCrear(request.POST, prefix='direcciones')

    if formulario.is_valid() and f_corr.is_valid() and f_tel.is_valid() and f_dir.is_valid():
        correos = _correos_activos(f_corr)
        tels    = _telefonos_activos(f_tel)
        dirs    = _direcciones_activas(f_dir)

        ok = True
        if len(correos) < 1:
            _poner_error_minimo(f_corr, 'Debes agregar al menos un correo.')
            ok = False
        if len(tels) < 1:
            _poner_error_minimo(f_tel, 'Debes agregar al menos un teléfono.')
            ok = False
        if len(dirs) < 1:
            _poner_error_minimo(f_dir, 'Debes agregar al menos una dirección.')
            ok = False

        if not ok:
            html = render_to_string('crud_personas/_form_persona.html', {
                'titulo_modal': 'Nuevo contacto',
                'formulario': formulario,
                'formset_correos': f_corr,
                'formset_telefonos': f_tel,
                'formset_direcciones': f_dir,
                'url_accion': request.path,
                'modo': 'crear',
            }, request=request)
            return JsonResponse({'ok': False, 'html': html})

        persona = formulario.save()

        for correo in correos:
            Correo.objects.create(persona=persona, correo=correo)
        for etiqueta, numero in tels:
            Telefono.objects.create(persona=persona, etiqueta=etiqueta, numero=numero)
        for d in dirs:
            Direccion.objects.create(persona=persona, **d)

        fila = render_to_string('crud_personas/_fila_persona.html', {'p': persona}, request=request)
        return JsonResponse({'ok': True, 'accion': 'crear', 'html_fila': fila})

    html = render_to_string('crud_personas/_form_persona.html', {
        'titulo_modal': 'Nuevo contacto',
        'formulario': formulario,
        'formset_correos': f_corr,
        'formset_telefonos': f_tel,
        'formset_direcciones': f_dir,
        'url_accion': request.path,
        'modo': 'crear',
    }, request=request)
    return JsonResponse({'ok': False, 'html': html})

@transaction.atomic
def modal_persona_editar(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)

    if request.method == 'GET':
        formulario, f_corr, f_tel, f_dir = _contexto_formularios(persona)
        html = render_to_string('crud_personas/_form_persona.html', {
            'titulo_modal': 'Editar contacto',
            'formulario': formulario,
            'formset_correos': f_corr,
            'formset_telefonos': f_tel,
            'formset_direcciones': f_dir,
            'url_accion': request.path,
            'modo': 'editar',
            'persona_obj': persona,
        }, request=request)
        return JsonResponse({'ok': True, 'html': html})

    formulario = PersonaFormulario(request.POST, request.FILES, instance=persona)
    f_corr = CorreoFormsetEditar(request.POST, instance=persona, prefix='correos')
    f_tel  = TelefonoFormsetEditar(request.POST, instance=persona, prefix='telefonos')
    f_dir  = DireccionFormsetEditar(request.POST, instance=persona, prefix='direcciones')

    if formulario.is_valid() and f_corr.is_valid() and f_tel.is_valid() and f_dir.is_valid():
        correos = _correos_activos(f_corr)
        tels    = _telefonos_activos(f_tel)
        dirs    = _direcciones_activas(f_dir)

        ok = True
        if len(correos) < 1:
            _poner_error_minimo(f_corr, 'Debes agregar al menos un correo.')
            ok = False
        if len(tels) < 1:
            _poner_error_minimo(f_tel, 'Debes agregar al menos un teléfono.')
            ok = False
        if len(dirs) < 1:
            _poner_error_minimo(f_dir, 'Debes agregar al menos una dirección.')
            ok = False

        if not ok:
            html = render_to_string('crud_personas/_form_persona.html', {
                'titulo_modal': 'Editar contacto',
                'formulario': formulario,
                'formset_correos': f_corr,
                'formset_telefonos': f_tel,
                'formset_direcciones': f_dir,
                'url_accion': request.path,
                'modo': 'editar',
                'persona_obj': persona,
            }, request=request)
            return JsonResponse({'ok': False, 'html': html})

        # Guardar persona
        persona = formulario.save()

        # BORRAR y RE-CREAR hijos según lo que venga en POST
        persona.correos.all().delete()
        persona.telefonos.all().delete()
        persona.direcciones.all().delete()

        for correo in correos:
            Correo.objects.create(persona=persona, correo=correo)
        for etiqueta, numero in tels:
            Telefono.objects.create(persona=persona, etiqueta=etiqueta, numero=numero)
        for d in dirs:
            Direccion.objects.create(persona=persona, **d)

        fila = render_to_string('crud_personas/_fila_persona.html', {'p': persona}, request=request)
        return JsonResponse({'ok': True, 'accion': 'editar', 'id': persona.id, 'html_fila': fila})

    html = render_to_string('crud_personas/_form_persona.html', {
        'titulo_modal': 'Editar contacto',
        'formulario': formulario,
        'formset_correos': f_corr,
        'formset_telefonos': f_tel,
        'formset_direcciones': f_dir,
        'url_accion': request.path,
        'modo': 'editar',
        'persona_obj': persona,
    }, request=request)
    return JsonResponse({'ok': False, 'html': html})

@transaction.atomic
def modal_persona_eliminar(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)
    if request.method == 'GET':
        html = render_to_string('crud_personas/_confirmar_eliminar.html', {
            'titulo_modal': 'Eliminar contacto',
            'persona': persona,
            'url_accion': request.path,
        }, request=request)
        return JsonResponse({'ok': True, 'html': html})

    pid = persona.id
    persona.delete()
    return JsonResponse({'ok': True, 'accion': 'eliminar', 'id': pid})
