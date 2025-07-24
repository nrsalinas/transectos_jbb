################################################################################
#
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <https://www.gnu.org/licenses/>. 
#
# Copyright 2025 Nelson R. Salinas
#
################################################################################

import streamlit as st
import pandas as pd
import gspread
import datetime
import pytz

gc = gspread.service_account_from_dict(st.secrets.credentials)
tz = pytz.timezone('America/Bogota')

if 'errors_site' not in st.session_state:
	st.session_state.errors_site = ''

if 'errors_rec' not in st.session_state:
	st.session_state.errors_rec = ''

if 'site_ok' not in st.session_state:
	st.session_state.site_ok = False

if 'rec_ok' not in st.session_state:
	st.session_state.rec_ok = False

if 'stage' not in st.session_state:
	st.session_state.stage = 'checking_site' # 'checking_record'

if 'submitted' not in st.session_state:
	st.session_state.submitted = False


##########     Object lists    ##############
#listas = pd.read_csv("Lista_categorias.csv")
tabla_sitios = pd.read_csv("sitios.csv")
tabla_sitios['name'] = tabla_sitios.codigo.apply(str) + '. ' + tabla_sitios.sitio.apply(str)
sitios = tabla_sitios.name.tolist()

wise_people = ['Lina Corrales', 'Esther Velásquez', 'Lina y Esther']

digitizers = ['Esther', 'Dana', 'Jose', 'Karen', 'Lina', 'Lizeth', 'MariaP', 'Natalia', 'Nelson']

cuadrants = [1, 2, 3]

id_observaciones = []

growth_forms = ['Árbol', 'Arbusto', 'Hierba', 'Enredadera', 'Epifita']

pheno = ['Estéril', 'Flor', 'Fruto']

st.markdown("""

# Jardín Botánico de Bogotá

## Programa Conservación _in situ_

### Formato de digitalización de transectos de vegetación.

#### Instrucciones

Inserte primero los datos pertinentes al sitio de estudio en la forma de abajo. Una vez termine de digitar los datos de un sitio, presione el botón :red[**Validar**] para validar los datos. Si existen errores, un mensaje aparecerá indicando la naturaleza del error. Si los datos son correctos, una nueva forma será desplegada con todos los campos relacionados con las propiedades del transecto y los individuos.

Al terminar de digitar todos los datos de un individuo presione el botón :red[**Validar**] de la segunda forma para verificar la información. Si existen errores a este nivel, la aplicación le indicará que se debe corregir. Si los datos del individuo son correctos, la aplicación desplegará los datos listos para ser insertados. Presione el botón :red[**Guardar**] para que la información sea enviada al repositorio remoto.

Cada vez que se envian datos al repositorio solo se limpia la forma de individuos, no la de sitio, por lo cual puede ingresar la información de todos los individuos de un transecto sin tener que digitar los datos del sitio de nuevo. Si quiere cambiar los datos de la localidad (por ejemplo, después de insertar todos los registros de un transecto y va a digitar la información de la siguiente unidad muestral), presione el botón :red[**Cambiar localidad**] y comience de nuevo.


""")

# This doesn't work in Linux -> :blue-background[:red[**Enviar**]] 

def validate_site():

	st.session_state.errors_site = ""
	in_trouble = False

	if st.session_state.token != st.secrets.token:
		st.session_state.errors_site += 'El token de autenticación es obligatorio.\n\n'
		in_trouble = True

	if st.session_state.date is None:
		st.session_state.errors_site += 'La fecha es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.time0 is None:
		st.session_state.errors_site += 'La hora inicial es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.timef is None:
		st.session_state.errors_site += 'La hora final es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.time0 and st.session_state.timef and \
		st.session_state.time0 >= st.session_state.timef:
		st.session_state.errors_site += 'La hora inicial debe ser menor a la hora final.\n\n'
		in_trouble = True

	if st.session_state.resp is None:
		st.session_state.errors_site += 'El nombre del responsable es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.digitizer is None:
		st.session_state.errors_site += 'El digitador es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.lon is None or st.session_state.lat is None:
		st.session_state.errors_site += "Las coordenadas geográficas son obligatorias.\n\n"
		in_trouble = True

	if st.session_state.site is None:
		st.session_state.errors_site += "El sitio es un campo obligatorio.\n\n"
		in_trouble = True

	if st.session_state.sector is None or len(st.session_state.sector) < 1:
		st.session_state.errors_site += "El sector es un campo obligatorio.\n\n"
		in_trouble = True

	if not in_trouble:
		st.session_state.site_ok = True

	st.session_state.submitted = False


def validate_rec():
	st.session_state.errors_rec = ""
	in_trouble = False

	# Número de transecto, hábito y morfo son obligatorios para todos los individuos, sean de cuadrantes o no
	if st.session_state.trans is None:
		st.session_state.errors_rec += 'El número de transecto es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.grow is None:
		st.session_state.errors_rec += 'El hábito es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.morfo is None or len(st.session_state.morfo) == 0:	
		st.session_state.errors_rec += 'El morfo o descripción de campo es un dato obligatorio.\n\n'
		in_trouble = True

	if st.session_state.cuadr:
		# Planta de cuadrante: solo es obligatorio hábito, morfo y cobertura
		if st.session_state.cober is None:
			st.session_state.errors_rec += 'El procentaje de cobertura es un dato obligatorio para las plantas de cuadrantes.\n\n'
			in_trouble = True

		if st.session_state.alt and st.session_state.alt > 0.5:
			st.session_state.errors_rec += 'Observaciones de cuadrantes solo son realizadas en individuos con alturas de máximo 0.5 m.\n\n'
			in_trouble = True

	else: 
		# Planta fuera de cuadrantes: todo es obligatorio, excepto cobertura
		if st.session_state.ind is None:
			st.session_state.errors_rec += 'El número de individuo es un campo obligatorio en individuos registrados por fuera de cuadrantes.\n\n'
			in_trouble = True

		if st.session_state.ubic is None:
			st.session_state.errors_rec += 'La ubicación del individuo es un campo obligatorio en individuos registrados por fuera de cuadrantes.\n\n'
			in_trouble = True

		if st.session_state.alt is None:
			st.session_state.errors_rec += 'La altura del individuo es un dato obligatorio en individuos registrados por fuera de cuadrantes.\n\n'
			in_trouble = True

		elif st.session_state.alt <= 0.5:
			st.session_state.errors_rec += 'Individuos de alturas menores o iguales a 0.5 m solo son registrados exclusivamente en cuadrantes.\n\n'
			in_trouble = True

		if st.session_state.copax is None or st.session_state.copay is None:
			st.session_state.errors_rec += 'Los diámetros de copas son obligatorios para individuos de alturas mayores a 0.5 m.\n\n'
			in_trouble = True


	if in_trouble:
		st.session_state.rec_ok = False
	else:
		st.session_state.rec_ok = True

	st.session_state.submitted = False

def set_site():
	st.session_state.site_ok = True


def submit():
	
	sh = gc.open_by_key(st.secrets.table_link).worksheet(st.session_state.digitizer)
	now = datetime.datetime.now(tz)
	row = [
		st.session_state.site,
		st.session_state.sector,
		st.session_state.resp,
	]

	if st.session_state.obs_site: 
		row.append(st.session_state.obs_site)
	else:
		row.append("")

	row += [
		str(st.session_state.date),
		str(st.session_state.time0),
		str(st.session_state.timef),
		st.session_state.lat,
		st.session_state.lon,
		st.session_state.trans]
	
	if st.session_state.cuadr:
		row.append(st.session_state.cuadr)
	else:
		row.append("")

	if st.session_state.ind:
		row.append(st.session_state.ind)
	else:
		row.append("")

	if st.session_state.ubic:
		row.append(st.session_state.ubic)
	else:
		row.append("")

	row.append(st.session_state.morfo)

	if st.session_state.alt:
		row.append(st.session_state.alt)
	else:
		row.append("")

	if st.session_state.copax:
		row.append(st.session_state.copax)
	else:
		row.append("")

	if st.session_state.copay: 
		row.append(st.session_state.copay)
	else:
		row.append("")

	if st.session_state.cober: 
		row.append(st.session_state.cober)
	else:
		row.append("")

	row.append(st.session_state.grow)

	if st.session_state.photo: 
		row.append(st.session_state.photo)
	else:
		row.append("")

	if st.session_state.obs_ind: 
		row.append(st.session_state.obs_ind)
	else:
		row.append("")
	
	row += [
		st.session_state.digitizer,
		now.strftime('%Y-%m-%d %H:%M:%S'),
	]
	
	sh.append_row(row)
	st.session_state.submitted = True
	clear_rec()


def clear_site():
	st.session_state.resp = None
	st.session_state.date = None
	st.session_state.time0 = None
	st.session_state.timef = None
	st.session_state.site = None
	st.session_state.sector = ''
	st.session_state.lat = None
	st.session_state.lon = None
	st.session_state.obs_site = ''
	st.session_state.site_ok = False

def clear_rec():
	st.session_state.trans = None
	st.session_state.cuadr = None
	st.session_state.ind = None
	st.session_state.ubic = None
	st.session_state.grow = None
	st.session_state.morfo = None
	st.session_state.copax = None
	st.session_state.copay = None
	st.session_state.cober = None
	st.session_state.photo = None
	st.session_state.obs_ind = None
	st.session_state.rec_ok = False


with st.form(
	"Transecto - sitio",
	clear_on_submit=False,
	):

	st.text_input(
		"Token de autenticación",
		help="Token de validación de usuario",
		placeholder='Digite el token',
		value=None,
		key="token"
	)

	st.selectbox(
		"Digitador", 
		digitizers, 
		index=None, 
		key='digitizer',
		placeholder="Seleccione un investigador",
		help='Persona que se encargó de digitar el formulario'
	)

	resp = st.selectbox(
		"Responsable", 
		wise_people, 
		index=None, 
		key='resp',
		placeholder="Seleccione un investigador",
		help='Persona que se encargó de dirigir la operación'
	)

	st.date_input(
		"Fecha",
		help="Fecha en la cual fue levantado el transecto.",
		value=None,
		key="date",
	)

	st.time_input(
		"Hora inicio",
		value=None,
		key="time0",
		step=900, # in secs : 15 mins
		help="Hora de inicio del transecto, en formato 24 horas."
	)

	st.time_input(
		"Hora final",
		value=None,
		key="timef",
		step=900, # in secs : 15 mins
		help="Hora de finalización del transecto, en formato 24 horas."
	)

	st.selectbox(
		"Sitio", 
		sitios, 
		index=None, 
		key='site',
		placeholder='Nombre del sitio de muestreo',
		help='Nombre estandarizado del lugar de muestreo'
	)

	st.text_input(
		"Sector",
		key='sector',
		value='',
		placeholder='Sector de muestreo',
		help='Nombre del sector de muestreo'
	)

	st.number_input(
		"Latitud", 
		key="lat",
		value=None,
		placeholder="Latitud",
		help='Latitud de ubicación del transecto en formato decimal (e.g., 3.09284)',
		max_value=4.838990,
		min_value=3.725902
	)

	st.number_input(
		"Longitud", 
		key="lon",
		value=None,
		placeholder="Longitud",
		help='Longitud de ubicación del transecto en formato decimal (e.g., -77.2360184)',
		min_value=-74.2248,
		max_value=-73.99194,
	)

	st.text_input(
		"Observaciones",
		key='obs_site',
		value=None,
		placeholder='Observaciones',
		help='Observaciones del sitio de muestreo.'
	)

	b0, b1 = st.columns([1, 1])

	with b0:
		st.form_submit_button('Validar', on_click=validate_site)

	with b1:
		st.form_submit_button('Cambiar localidad', on_click=clear_site)


rec_cont = st.empty()

if st.session_state.site_ok:

	with rec_cont.form(
	#with st.form(
		"Transecto - registros",
		clear_on_submit=False
	):

		st.number_input(
			"Transecto",
			key='trans',
			value=None,
			step=1,
			min_value=1,
			placeholder="Número de transecto",
			help='Identificador del transecto',
		)

		st.selectbox(
			"Cuadrante",
			cuadrants,
			key='cuadr',
			index=None,
			placeholder="Número del cuadrante",
			help='Identificador del cuadrante',
		)

		st.number_input(
			"Individuo",
			key='ind',
			value=None,
			step=1,
			min_value=1,
			placeholder="Número de individuo",
			help='Identificador del individuo en el transecto',
		)

		st.number_input(
			"Ubicación",
			key='ubic',
			value=None,
			step=0.1,
			min_value=0.0,
			max_value=50.0,
			placeholder="Ubicación del individuo",
			help='Ubicación del individuo a lo largo del transecto, en metros',
		)

		st.selectbox(
			"Hábito", 
			growth_forms,
			index=None, 
			key='grow',
			placeholder="Seleccione un hábito",
			help='Hábito de acuerdo a la documentación del proyecto.'
		)

		st.text_input(
			"Morfo",
			key='morfo',
			value=None,
			placeholder='Morfo',
			help='Descripción o identificación de campo de la especie.'
		)

		st.number_input(
			"Altura",
			key='alt',
			value=None,
			step=0.1,
			placeholder="Altura del individuo (m)",
			help='Altura del individuo, proyeccción perpendicular en relación al substrato.',
		)

		st.number_input(
			"Copa X",
			key='copax',
			value=None,
			step=1,
			placeholder="Diámetro de la copa (cm)",
			help='Diámetro de la copa del individuo a lo largo del eje horizontal de la parcela (cm).',
		)

		st.number_input(
			"Copa Y",
			key='copay',
			value=None,
			step=1,
			placeholder="Diámetro de la copa (cm)",
			help='Diámetro de la copa del individuo a lo largo del eje vertical de la parcela (cm).',
		)

		st.number_input(
			"Cobertura",
			key='cober',
			value=None,
			min_value=1,
			max_value=100,
			step=1,
			placeholder="Cobertura del individuo en la parcela (%)",
			help='Porcentaje del área del cuadrante que cubre el individuo. Posibles valores: 1-100%.',
		)

		st.text_input(
			"Foto",
			key='photo',
			value=None,
			placeholder='Fotografía del individuo',
			help='Nombre del archivo fotográfico.'
		)

		st.text_input(
			"Observaciones",
			key='obs_ind',
			value=None,
			placeholder='Observaciones',
			help='Observaciones del individuo.'
		)

		st.form_submit_button('Validar', on_click=validate_rec)

	pretty_data = st.empty()

	if st.session_state.rec_ok:

		with pretty_data.container():

			bits = [
				"Confirmación de la información digitada.\n",
				f"Responsable(s): {st.session_state.resp}",
				f"Fecha: {st.session_state.date}",
				f"Hora inicial: {st.session_state.time0}",
				f"Hora final: {st.session_state.timef}",
				f"Sitio: {st.session_state.site}",
				f"Sector: {st.session_state.sector}",
				f"Latitud: {st.session_state.lat}",
				f"Longitud: {st.session_state.lon}",
				f"Transecto: {st.session_state.trans}",
				f"Cuadrante: {st.session_state.cuadr}",
				f"Ubicación: {st.session_state.ubic}",
				f"Individuo: {st.session_state.ind}",
				f"Hábito: {st.session_state.grow}",
				f"Morfo: {st.session_state.morfo}",
				f"Altura: {st.session_state.alt}",
				f"Copa X: {st.session_state.copax}",
				f"Copa Y: {st.session_state.copay}",
				f"Cobertura: {st.session_state.cober}",
				f"Observaciones individuo: {st.session_state.obs_ind}",
			]

			st.markdown("\n\n".join(bits))

			st.markdown("""Si los datos arriba son correctos, presione el botón :red[**Guardar**] para enviar los datos.""")

			st.button("Guardar", on_click=submit)

		if st.session_state.submitted:
			pretty_data.empty()

	else:	
		if len(st.session_state.errors_rec) > 0:
			st.session_state.errors_rec = "# Error\n\n" + st.session_state.errors_rec
			st.info(st.session_state.errors_rec)

		else:
			pretty_data.empty()

elif len(st.session_state.errors_site) > 0:
	st.session_state.errors_site = "# Error\n\n" + st.session_state.errors_site
	st.info(st.session_state.errors_site)

else: 
	rec_cont.empty()

exit(0)