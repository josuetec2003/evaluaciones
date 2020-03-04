from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Max
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from .models import Periodo, Variable, Docente, Asignatura, Evaluacion, DetalleEvaluacion
from .forms import MyAuthForm
from ast import literal_eval
from .utils import render_to_pdf_utf8


@login_required()
def log_out(request):
	logout(request)
	return HttpResponseRedirect('/')


def log_in(request):
	if request.method == 'POST':
		form = MyAuthForm(request=request, data=request.POST)

		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')

			user = authenticate(username = request.POST['username'], password = request.POST['password'])

			if user is not None:
				if user.is_active:
					login(request, user)		 

					if request.GET.get('next'):
						return HttpResponseRedirect(request.GET.get('next'))
					else:
						return HttpResponseRedirect(reverse('home'))
				else:
					return HttpResponse('Tu usuario fue desactivado')
			else:
				return render(request, 'index.html', {'form': form})
		else:
			return render(request, 'index.html', {'form': form})
	else:
		return HttpResponseRedirect(reverse('home'))



def home(request):
	if request.user.is_authenticated:
		request.session['page'] = 'home'
		anio = datetime.now().year
		periodo = Periodo.objects.filter(anio=anio).annotate(Max('numero'))[0]
		variables = Variable.objects.filter(estado=True)
		docentes = Docente.objects.filter(estado=True)
		asignaturas = Asignatura.objects.all().order_by('nombre')

		ctx = {
			'periodo': periodo,
			'fecha': datetime.now().strftime('%Y-%m-%d'),
			'variables': variables,
			'docentes': docentes,
			'asignaturas': asignaturas
		}

		return render(request, 'evaluar.html', ctx)
	else:
		form = MyAuthForm()
		return render(request, 'index.html', {'form': form})


@login_required()
def guardar_evaluacion(request):
	if request.is_ajax():
		fecha = request.GET.get('fecha')
		periodo = Periodo.objects.get(pk=request.GET.get('periodo'))
		docente = Docente.objects.get(pk=request.GET.get('docente'))
		asignatura = Asignatura.objects.get(pk=request.GET.get('asignatura'))
		evaluacion = literal_eval(request.GET.get('evaluacion'))

		# verifica que el docente ya tenga la evaluada la clase en el periodo actual
		evaluacion_clase = Evaluacion.objects.filter(docente=docente, asignatura=asignatura, periodo=periodo)

		if evaluacion_clase:
			return JsonResponse({'OK': False, 'msj': f'[ {docente.nombre} ] ya tiene evaluada la clase [ {asignatura.nombre} ] en el [ Periodo {periodo} ]'})

		evaluar = Evaluacion(
			fecha = fecha,
			docente = docente,
			asignatura = asignatura,
			periodo = periodo
		)
		evaluar.save()

		evaluaciones = []

		try:
			for e in evaluacion:
				evaluaciones.append(
					DetalleEvaluacion(
						evaluacion = evaluar, 
						variable = Variable.objects.get(pk = e['variable_id']),
						calificacion = e['nota'],
						observacion = e['observacion']

					)
				)

			DetalleEvaluacion.objects.bulk_create(evaluaciones)

			return JsonResponse({'OK': True, 'msj': 'La evaluación ha sido registrada'})

		except Exception as e:
			return JsonResponse({'OK': False, 'msj': str(e)})


@login_required()
def evaluaciones(request):
	request.session['page'] = 'evaluaciones'

	periodos = Periodo.objects.all().order_by('-anio', '-numero')

	pid = request.GET.get('pid')
	lista_evals = []

	if pid:
		periodo = Periodo.objects.get(pk=pid)
		evals = Evaluacion.objects.filter(periodo = periodo).order_by('-fecha')

		lista_evals = []

		for e in evals:
			variables = e.detalleevaluacion_set.all()
			acum_eva = 0
			acum_max = 0

			for v in variables:
				acum_eva += v.calificacion
				acum_max += 5

			prom = (acum_eva / acum_max) * 100

			lista_evals.append({
				'id': e.id,
				'fecha': e.fecha,
				'docente': e.docente,
				'asignatura': e.asignatura,
				'calificacion': round(prom, 2)
			})

	else:
		anio = datetime.now().year
		periodo = Periodo.objects.filter(anio=anio).annotate(Max('numero'))[0]
		evals = Evaluacion.objects.filter(periodo = periodo).order_by('-fecha')

		for e in evals:
			variables = e.detalleevaluacion_set.all()
			acum_eva = 0
			acum_max = 0

			for v in variables:
				acum_eva += v.calificacion
				acum_max += 5

			prom = (acum_eva / acum_max) * 100

			lista_evals.append({
				'id': e.id,
				'fecha': e.fecha,
				'docente': e.docente,
				'asignatura': e.asignatura,
				'calificacion': round(prom, 2)
			})

	ctx = {
		'periodos': periodos,
		'periodo': periodo,
		'evals': lista_evals
	}

	return render(request, 'evaluaciones.html', ctx)


@login_required()
def evaluacion(request, id):
	e = Evaluacion.objects.get(pk=id)
	ctx = {
		'e': e,
		'logo': f'{settings.STATIC_ROOT}/app/img/logo.png'
	}

	pdf = render_to_pdf_utf8('formato_pdf.html', ctx)

	if pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "evaluacion.pdf"
		content = "inline; filename=%s" % (filename)

		if request.GET.get("action") == 'download':
			content = "attachment; filename=%s" %(filename)

		response['Content-Disposition'] = content
		return response

	return HttpResponse("Not found")



@login_required()
def mejor_docente(request):
	request.session['page'] = 'mejor_docente'

	anio = datetime.now().year
	periodo = Periodo.objects.filter(anio=anio).annotate(Max('numero'))[0]

	evaluaciones = Evaluacion.objects.filter(periodo=periodo)
	docentes_id = list(evaluaciones.values_list('docente', flat=True).distinct())

	evaluacion_x_docente = []

	# iterar los docentes evaluados en el periodo actual
	for id in docentes_id:
		docente = Docente.objects.get(pk=id)
		evals 	= Evaluacion.objects.filter(periodo=periodo, docente=docente)

		# acumula el total de cada evaluacion del docente
		acum_evals = 0

		# iterar las evaluaciones del docente
		for e in evals:
			variables = e.detalleevaluacion_set.all()
			acum_eva = 0
			acum_max = 0

			for v in variables:
				acum_eva += v.calificacion
				acum_max += 5

			prom = (acum_eva / acum_max) * 100
			acum_evals += prom

		prom_general = acum_evals / evals.count()

		evaluacion_x_docente.append({
			'docente': docente,
			'facultad': docente.facultad.nombre_completo,
			'promedio': round(prom_general, 2)
		})


	evaluacion_x_docente = sorted(evaluacion_x_docente, key = lambda i: (i['facultad'], -i['promedio']))

	ctx = {
		'periodo': periodo,
		'evaluaciones': evaluacion_x_docente
	}

	return render(request, 'mejor_docente.html', ctx)






