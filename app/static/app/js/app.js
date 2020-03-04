$(function () {

	$('#btn-guardar-eval').on('click', function () {
		var $me = $(this);
		var url = $me.data('url');
		var $fecha = $('#txt-fecha');
		var $docente = $('#cbo-docente');
		var $asignatura = $('#cbo-asignatura');
		

		if ($fecha.val() === '')
		{
			notify('warn', 'Debe seleccionar una fecha');
			$fecha.focus();
			return;
		}

		if ($docente.val() === '')
		{
			notify('warn', 'Debe seleccionar al docente que será evaluado');
			$docente.trigger('chosen:activate');
			return;
		}

		if ($asignatura.val() === '')
		{
			notify('warn', 'Debe seleccionar la asignatura que será evaluada');
			$asignatura.trigger('chosen:activate');;
			return;
		}

		$me.attr('disabled', true);

		var data  = [];
		var filas = $('.fila-variable');
		var $fila;
		// $("input[name='gender']:checked").val();

		for (let fila of filas)
		{
			$fila = $(fila);
			var nota = $fila.find(`input[name="variable-${$fila.data('idv')}"]:checked`).val();
			var obsv = $fila.find('.txt-observaciones').val();

			if (nota !== undefined)
			{
				data.push({
					'variable_id': $fila.data('idv'),
					'nota': parseInt(nota),
					'observacion': obsv
				});				
			}
		}

		if (data.length !== filas.length)
		{
			notify('warn', 'Hay variables sin evaluar, por favor verifique!');
			$me.removeAttr('disabled');
		} else {

			var ctx = {
				'fecha': $fecha.val(),
				'docente': $docente.val(),
				'asignatura': $asignatura.val(),
				'periodo': $('#txt-periodo').val(),
				'evaluacion': JSON.stringify(data)
			};

			$.get(url, ctx, function (response) {
				if (response.OK)
				{
					notify('success', response.msj);

					setTimeout(function () {
						location.reload();
					}, 3000)
				} else {
					notify('error', response.msj);
					$me.removeAttr('disabled');
				}
			}, 'json');

		}

	});

});

function notify (style, msg)
{
  $.notify.defaults({ className: style });
  $.notify(msg, {position: 'bottom'});
}