(function(){
  let modal, cropper = null;

  function csrftoken(){
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  function abrirModal(url){
    $.get(url)
     .done(function(resp){
       if(resp && resp.ok){
         $('#modalContenido').html(resp.html);
         if(!modal){ modal = new bootstrap.Modal(document.getElementById('modalGeneral')); }
         modal.show();
         inicializarDentroModal();
       } else {
         alert('No se pudo abrir el formulario.');
       }
     })
     .fail(function(xhr){
       console.error('[modales] Falló GET', xhr.status, xhr.responseText);
       alert('Error al cargar el modal (' + xhr.status + '). Revisa la consola.');
     });
  }

  function getPrefix($cont){
    const $total = $cont.find('input[name$="-TOTAL_FORMS"]');
    const name = $total.attr('name') || '';
    return name.replace('-TOTAL_FORMS','');
  }
  function getTotalField($cont){
    const prefix = getPrefix($cont);
    return $cont.find(`input[name="${prefix}-TOTAL_FORMS"]`);
  }
  function getNextIndex($cont){
    return parseInt(getTotalField($cont).val() || '0', 10);
  }
  function setTotal($cont, val){
    getTotalField($cont).val(val);
  }

  function replNameIndex(val, prefix, idx){
    if(!val) return val;
    return val.replace(new RegExp('^' + prefix + '-(\\d+)-'), `${prefix}-${idx}-`);
  }
  function replIdIndex(val, prefix, idx){
    if(!val) return val;
    return val.replace(new RegExp('^id_' + prefix + '-(\\d+)-'), `id_${prefix}-${idx}-`);
  }

  function esInicial($item){
    const $hid = $item.find('input[type="hidden"][name$="-id"]');
    return $hid.length && ($hid.val() || '').trim() !== '';
  }

  function marcarInicialBorrado($item){
    let $del = $item.find('input[type="hidden"][name$="-DELETE"]');
    if(!$del.length){
      const anyInput = $item.find('input,select,textarea').first();
      const base = (anyInput.attr('name') || '').replace(/([^-]+)-(\d+)-.*/, '$1-$2-');
      $del = $(`<input type="hidden" name="${base}DELETE" value="on">`);
      $item.append($del);
    } else {
      $del.val('on');
    }
    $item.addClass('opacity-50 d-none');
  }

  function reindexSoloNuevos($cont){
    const prefix = getPrefix($cont);
    const $items = $cont.find('.js-formset-item');
    let iniciales = [], nuevos = [];

    $items.each(function(){
      (esInicial($(this)) ? iniciales : nuevos).push(this);
    });

    const base = iniciales.length;
    nuevos.forEach(function(node, i){
      const $it = $(node);
      $it.find('input,select,textarea,label').each(function(){
        const n = $(this).attr('name');
        const id = $(this).attr('id');
        const fr = $(this).attr('for');
        if(n){ $(this).attr('name', replNameIndex(n, prefix, base+i)); }
        if(id){ $(this).attr('id',   replIdIndex(id, prefix, base+i)); }
        if(fr){ $(this).attr('for',  replIdIndex(fr, prefix, base+i)); }
      });
    });

    setTotal($cont, iniciales.length + nuevos.length);
  }

  function crearFilaNueva($cont){
    const idCont  = $cont.attr('id');
    const prefix  = getPrefix($cont);
    const idx     = getNextIndex($cont);

    let html = '';
    if(idCont === 'correosFormset'){
      html = `
        <div class="row g-2 align-items-center formset-item js-formset-item">
          <div class="col-10">
            <input type="email" name="${prefix}-${idx}-correo" id="id_${prefix}-${idx}-correo"
                  class="form-control" placeholder="correo@dominio.com">
          </div>
          <div class="col-2 text-end">
            <button type="button" class="btn btn-sm btn-outline-danger js-remover-form">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>`;
    } else if(idCont === 'telefonosFormset'){
      html = `
        <div class="row g-2 align-items-center formset-item js-formset-item">
          <div class="col-5">
            <input type="text" name="${prefix}-${idx}-etiqueta" id="id_${prefix}-${idx}-etiqueta"
                  class="form-control" placeholder="casa, oficina, celular...">
          </div>
          <div class="col-5">
            <input type="text" name="${prefix}-${idx}-numero" id="id_${prefix}-${idx}-numero"
                  class="form-control" placeholder="0000000000"
                  inputmode="numeric" maxlength="10" pattern="\\d{1,10}">
          </div>
          <div class="col-2 text-end">
            <button type="button" class="btn btn-sm btn-outline-danger js-remover-form">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>`;
    } else if(idCont === 'direccionesFormset'){
      html = `
        <div class="formset-item js-formset-item">
          <label for="id_${prefix}-${idx}-linea1">Calle y número</label>
          <input type="text" name="${prefix}-${idx}-linea1" id="id_${prefix}-${idx}-linea1" class="form-control">
          <label for="id_${prefix}-${idx}-linea2">Colonia / Depto.</label>
          <input type="text" name="${prefix}-${idx}-linea2" id="id_${prefix}-${idx}-linea2" class="form-control">
          <div class="row g-2">
            <div class="col-6">
              <label for="id_${prefix}-${idx}-ciudad">Ciudad</label>
              <input type="text" name="${prefix}-${idx}-ciudad" id="id_${prefix}-${idx}-ciudad" class="form-control">
            </div>
            <div class="col-6">
              <label for="id_${prefix}-${idx}-estado">Estado</label>
              <input type="text" name="${prefix}-${idx}-estado" id="id_${prefix}-${idx}-estado" class="form-control">
            </div>
          </div>
          <div class="row g-2">
            <div class="col-6">
              <label for="id_${prefix}-${idx}-cp">C.P.</label>
              <input type="text" name="${prefix}-${idx}-cp" id="id_${prefix}-${idx}-cp"
                    class="form-control" inputmode="numeric" pattern="\\d*">
            </div>
            <div class="col-6">
              <label for="id_${prefix}-${idx}-pais">País</label>
              <input type="text" name="${prefix}-${idx}-pais" id="id_${prefix}-${idx}-pais" class="form-control">
            </div>
          </div>
          <div class="text-end mt-2">
            <button type="button" class="btn btn-outline-danger btn-sm js-remover-form">
              <i class="bi bi-trash"></i> Eliminar
            </button>
          </div>
        </div>`;
    }

    const $nueva = $(html);
    $cont.append($nueva);
    setTotal($cont, idx + 1);
    engancharTelefonos($nueva);
    engancharCPs($nueva);
    engancharCorreos($nueva);
    enlazarRemover();
    validarYToggleBoton($('#modalContenido'));
  }

  function enlazarRemover(){
    $('.js-remover-form').off('click.remF').on('click.remF', function(){
      const $cont = $(this).closest('#correosFormset, #telefonosFormset, #direccionesFormset');
      const $item = $(this).closest('.js-formset-item');
      if (esInicial($item)) {
        marcarInicialBorrado($item);
        validarYToggleBoton($('#modalContenido'));
      } else {
        $item.remove();
        reindexSoloNuevos($cont);
        validarYToggleBoton($('#modalContenido'));
      }
    });
  }

  function engancharTelefonos($ctx){
    const $inputs = $ctx.find('input[name$="-numero"]');
    $inputs.attr({ inputmode: 'numeric', maxlength: '10', pattern: '\\d{1,10}' });
    $inputs.off('.soloNumTel').on('beforeinput.soloNumTel', function(e){
      if(e.originalEvent && e.originalEvent.data && /\D/.test(e.originalEvent.data)){ e.preventDefault(); }
    }).on('input.soloNumTel paste.soloNumTel', function(){
      const limpio = this.value.replace(/\D+/g, '').slice(0, 10);
      if(this.value !== limpio) this.value = limpio;
      validarYToggleBoton($('#modalContenido'));
    });
  }

  function engancharCPs($ctx){
    const $inputs = $ctx.find('input[name$="-cp"]');
    $inputs.attr({ inputmode: 'numeric', pattern: '\\d*' });
    $inputs.off('.soloNumCP').on('beforeinput.soloNumCP', function(e){
      if(e.originalEvent && e.originalEvent.data && /\D/.test(e.originalEvent.data)){ e.preventDefault(); }
    }).on('input.soloNumCP paste.soloNumCP', function(){
      const limpio = this.value.replace(/\D+/g, '');
      if(this.value !== limpio) this.value = limpio;
      validarYToggleBoton($('#modalContenido'));
    });
  }

  function engancharCorreos($ctx){
    const $inputs = $ctx.find('input[type="email"], input[name$="-correo"]');
    $inputs.each(function(){ if(this.type !== 'email') this.type = 'email'; });
    $inputs.off('.valCorreo').on('input.valCorreo blur.valCorreo', function(){
      marcarInvalidoCorreo($(this));
      validarYToggleBoton($('#modalContenido'));
    });
  }

  function marcarInvalidoCorreo($input){
    if($input[0].checkValidity()){
      $input.removeClass('is-invalid');
      if($input.next('.invalid-feedback').length) $input.next('.invalid-feedback').addClass('d-none');
    } else {
      $input.addClass('is-invalid');
      if(!$input.next('.invalid-feedback').length){
        $input.after('<div class="invalid-feedback">Ingresa un correo válido.</div>');
      } else {
        $input.next('.invalid-feedback').removeClass('d-none');
      }
    }
  }

  function validarYToggleBoton($ctx){
    const $btnGuardar = $ctx.find('#formPersona button[type="submit"]');
    let correosInvalidos = false, correosActivos = 0;
    $('#correosFormset .js-formset-item').each(function(){
      const $it = $(this);
      const borrado = $it.find('input[type="hidden"][name$="-DELETE"]').val() === 'on';
      if (borrado) return;
      const $mail = $it.find('input[name$="-correo"]');
      const val = ($mail.val() || '').trim();
      if (val){
        if(!$mail[0].checkValidity()) correosInvalidos = true;
        correosActivos += 1;
      }
    });

    let telsActivos = 0;
    $('#telefonosFormset .js-formset-item').each(function(){
      const $it = $(this);
      const borrado = $it.find('input[type="hidden"][name$="-DELETE"]').val() === 'on';
      if (borrado) return;
      const val = ($it.find('input[name$="-numero"]').val() || '').trim();
      if (val) telsActivos += 1;
    });

    let dirsActivos = 0;
    $('#direccionesFormset .js-formset-item').each(function(){
      const $it = $(this);
      const borrado = $it.find('input[type="hidden"][name$="-DELETE"]').val() === 'on';
      if (borrado) return;
      const val = ($it.find('input[name$="-linea1"]').val() || '').trim();
      if (val) dirsActivos += 1;
    });

    $('#errMinCorreos').toggleClass('d-none', correosActivos >= 1 && !correosInvalidos);
    $('#errMinTelefonos').toggleClass('d-none', telsActivos >= 1);
    $('#errMinDirecciones').toggleClass('d-none', dirsActivos >= 1);

    const ok = (correosActivos >= 1) && !correosInvalidos && (telsActivos >= 1) && (dirsActivos >= 1);
    $btnGuardar.prop('disabled', !ok);
  }

  function engancharFormsetsDinamicos(){
    $('.js-agregar-form').off('click.addForm').on('click.addForm', function(){
      const $cont = $($(this).data('target'));
      crearFilaNueva($cont);
    });

    enlazarRemover();
  }

  function enlazarRemover(){
    $('.js-remover-form').off('click.remF').on('click.remF', function(){
      const $cont = $(this).closest('#correosFormset, #telefonosFormset, #direccionesFormset');
      const $item = $(this).closest('.js-formset-item, .js-formset-item.border');

      if (esInicial($item)) {
        marcarInicialBorrado($item);
        validarYToggleBoton($('#modalContenido'));
      } else {
        $item.remove();
        reindexSoloNuevos($cont);
        validarYToggleBoton($('#modalContenido'));
      }
    });
  }

  function inicializarDentroModal(){
    const $ctx = $('#modalContenido');
    const inputReal = $ctx.find('#id_fotografia');
    const contCropper = $ctx.find('#contenedorCropper');
    const imgCropper  = $ctx.find('#imgCropper');
    const btnAplicar  = $ctx.find('#btnAplicarRecorte');
    const btnCancelar = $ctx.find('#btnCancelarRecorte');
    const preview     = $ctx.find('#previewFoto');
    const ocultoBase64 = $ctx.find('input[name="imagen_recortada"]');

    if(inputReal.length){
      inputReal.off('change.crop').on('change.crop', function(e){
        const file = e.target.files[0]; if(!file) return;
        const reader = new FileReader();
        reader.onload = function(ev){
          imgCropper.attr('src', ev.target.result);
          contCropper.removeClass('d-none'); btnAplicar.removeClass('d-none'); btnCancelar.removeClass('d-none');
          if(cropper){ cropper.destroy(); cropper = null; }
          cropper = new Cropper(imgCropper[0], { aspectRatio: 1, viewMode: 1, autoCropArea: 1 });
        };
        reader.readAsDataURL(file);
      });
    }
    btnAplicar && btnAplicar.off('click.cropUse').on('click.cropUse', function(){
      if(!cropper) return;
      const canvas = cropper.getCroppedCanvas({width: 400, height: 400});
      const dataUrl = canvas.toDataURL('image/png');
      ocultoBase64.val(dataUrl); preview.attr('src', dataUrl);
      try { inputReal.val(''); } catch(e){}
      cropper.destroy(); cropper = null;
      $ctx.find('#contenedorCropper, #btnAplicarRecorte, #btnCancelarRecorte').addClass('d-none');
    });
    btnCancelar && btnCancelar.off('click.cropCancel').on('click.cropCancel', function(){
      if(cropper){ cropper.destroy(); cropper = null; }
      contCropper.addClass('d-none'); btnAplicar.addClass('d-none'); btnCancelar.addClass('d-none');
    });

    engancharTelefonos($ctx);
    engancharCPs($ctx);
    engancharCorreos($ctx);
    engancharFormsetsDinamicos();
    validarYToggleBoton($ctx);

    $ctx.find('#formPersona').off('submit.ajax').on('submit.ajax', function(e){
      e.preventDefault();
      const $form = $(this);
      const fd = new FormData(this);
      $.ajax({
        url: $form.attr('action'), method: 'POST', data: fd, processData: false, contentType: false,
        headers: {'X-CSRFToken': csrftoken(), 'X-Requested-With': 'XMLHttpRequest'},
        success: function(resp){
          if(resp.ok){
            if(resp.accion === 'crear'){
              if($('#tbodyPersonas .js-fila-vacia').length){ $('#tbodyPersonas .js-fila-vacia').remove(); }
              $('#tbodyPersonas').prepend(resp.html_fila);
            } else if(resp.accion === 'editar'){
              $('#fila-'+resp.id).replaceWith(resp.html_fila);
            }
            modal.hide();
          } else {
            $('#modalContenido').html(resp.html);
            inicializarDentroModal();
          }
        }
      });
    });

    $ctx.find('#formEliminar').off('submit.del').on('submit.del', function(e){
      e.preventDefault();
      const $form = $(this);
      $.ajax({
        url: $form.attr('action'), method: 'POST', data: $form.serialize(),
        headers: {'X-CSRFToken': csrftoken(), 'X-Requested-With': 'XMLHttpRequest'},
        success: function(resp){
          if(resp.ok && resp.accion === 'eliminar'){
            $('#fila-'+resp.id).remove();
            if($('#tbodyPersonas tr').length === 0){
              $('#tbodyPersonas').append('<tr class="js-fila-vacia"><td colspan="5" class="text-center text-muted p-4">Sin registros…</td></tr>');
            }
            modal.hide();
          }
        }
      });
    });

    if ($('#errMinCorreosSrv').length)   { $('#errMinCorreos').addClass('d-none'); }
    if ($('#errMinTelefonosSrv').length) { $('#errMinTelefonos').addClass('d-none'); }
    if ($('#errMinDireccionesSrv').length){ $('#errMinDirecciones').addClass('d-none'); }
  }

  $(document).on('click', '.js-abrir-modal', function(e){
    e.preventDefault();
    const url = $(this).data('url') || $(this).attr('href');
    if(url) abrirModal(url);
  });

  $(function(){
    console.log('[modales_persona.js] cargado');
  });
})();
