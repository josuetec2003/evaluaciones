from django.db import models

class Facultad(models.Model):
	nombre_completo = models.CharField(max_length=100)
	nombre_corto = models.CharField(max_length=30)

	def __str__(self):
		return self.nombre_completo

class Docente(models.Model):
	nombre = models.CharField(max_length=30)
	apellido = models.CharField(max_length=30)
	estado = models.BooleanField(default=True)
	facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f'{self.nombre} {self.apellido} ({self.facultad.nombre_corto})'

class Asignatura(models.Model):
	codigo = models.CharField(max_length=6, unique=True)
	nombre = models.CharField(max_length=60)

	def __str__(self):
		return f'{self.codigo} - {self.nombre}'

class Periodo(models.Model):
	numero = models.SmallIntegerField()
	anio = models.SmallIntegerField()

	def __str__(self):
		return f'{self.numero}, {self.anio}'

class Variable(models.Model):
	descripcion = models.TextField()
	estado = models.BooleanField(default=True)

	def __str__(self):
		return f'{self.descripcion} - {self.estado}'

class Evaluacion(models.Model):
	fecha = models.DateField()
	docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
	periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.fecha} | {self.docente} | {self.asignatura} | {self.periodo}'

class DetalleEvaluacion(models.Model):
	evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
	variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
	calificacion = models.SmallIntegerField(null=True, blank=True)
	observacion = models.TextField(null=True, blank=True)

	def __str__(self):
		return f'{self.evaluacion.id} - ({self.calificacion}) - {self.variable} ({self.observacion})'


