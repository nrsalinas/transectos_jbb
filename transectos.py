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

gc = gspread.service_account_from_dict(st.secrets.credentials)

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

digitizers = ['Esther', 'Dana', 'Jose', 'Lina', 'MariaP', 'Natalia', 'Nelson']

subplots = ['2x2', '3x3', '6x6', '13x13', '20x20']

id_observaciones = []

growth_forms = ['Árbol', 'Arbusto', 'Hierba', 'Enredadera']

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

	if st.session_state.par is None:
		st.session_state.errors_rec += 'El número de parcela es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.subpar is None:
		st.session_state.errors_rec += 'La categoría de subparcela es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.ind is None:
		st.session_state.errors_rec += 'El número de individuo es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.grow is None:
		st.session_state.errors_rec += 'La forma de crecimiento es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.morfo is None:	
		st.session_state.errors_rec += 'El morfo o descripción de campo es un dato obligatorio.\n\n'
		in_trouble = True

	if st.session_state.subpar in ['3x3', '6x6', '13x13', '20x20'] and \
		st.session_state.alt is None:

		st.session_state.errors_rec += 'La altura del individuo es un campo obligatorio para subparcelas no herbáceas rasantes.\n\n'
		in_trouble = True

	elif st.session_state.subpar == '3x3' and (st.session_state.alt < 0.5 or st.session_state.alt > 1.5):

		st.session_state.errors_rec += 'La altura del individuo está por fuera del rango aceptable para la clase de subparcela.\n\n'
		in_trouble = True


	if st.session_state.subpar in ['6x6', '13x13', '20x20'] and st.session_state.cap is None:
		st.session_state.errors_rec += 'La circuferencia a la altura de pecho es un campo obligatorio para subparcelas no herbáceas.\n\n'
		in_trouble = True

	elif st.session_state.subpar == '6x6' and (st.session_state.cap < (2.5 / 3.14159) or st.session_state.cap > (5 / 3.14159)):
		st.session_state.errors_rec += 'El CAP del individuo está por fuera del rango aceptable para la clase de subparcela.\n\n'
		in_trouble = True

	elif st.session_state.subpar == '13x13' and (st.session_state.cap < (5 / 3.14159) or st.session_state.cap > (10 / 3.14159)):
		st.session_state.errors_rec += 'El CAP del individuo está por fuera del rango aceptable para la clase de subparcela.\n\n'
		in_trouble = True

	elif st.session_state.subpar == '20x20' and (st.session_state.cap < (10 / 3.14159)):
		st.session_state.errors_rec += 'El CAP del individuo está por fuera del rango aceptable para la clase de subparcela.\n\n'
		in_trouble = True

	if st.session_state.subpar in ['3x3', '6x6', '13x13', '20x20'] and st.session_state.copax is None:
		st.session_state.errors_rec += 'El diámetro de copa horizontal es un campo obligatorio para subparcelas no herbáceas rasantes.\n\n'
		in_trouble = True

	if st.session_state.subpar in ['3x3', '6x6', '13x13', '20x20'] and st.session_state.copay is None:
		st.session_state.errors_rec += 'El diámetro de copa vertical es un campo obligatorio para subparcelas no herbáceas rasantes.\n\n'
		in_trouble = True

	if st.session_state.subpar == '2x2' and st.session_state.cober is None:
		st.session_state.errors_rec += 'La cobertura es un campo obligatorio para subparcelas de herbáceas rasantes.\n\n'
		in_trouble = True

	if st.session_state.pheno is None:
		st.session_state.errors_rec += 'La fenología es un campo obligatorio.\n\n'
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
	now = datetime.datetime.now()
	#Sitio	Sector	Responsables	Observaciones sitio	Fecha	Hora inicio	Hora final	Latitud	Longitud	# Parcela	Subparcela	# ind.	Forma crecimiento	Morfo	Altura (m)	CAP (cm)	Copa X (cm)	Copa Y (cm)	% Cobertura	Fenología	% Fenología	Observaciones individuo	Digitador	Fecha digitación
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
		st.session_state.par,
		st.session_state.subpar,
		st.session_state.ind,
		st.session_state.grow,
		st.session_state.morfo,
		st.session_state.alt,
	]

	if st.session_state.cap: 
		row.append(st.session_state.cap)
	else:
		row.append("")

	row += [
		st.session_state.copax,
		st.session_state.copay,
		st.session_state.cober,
		st.session_state.pheno,
	]
	
	if st.session_state.per_pheno: 
		row.append(st.session_state.per_pheno)
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
		clear_on_submit=True
	):

		st.number_input(
			"Parcela",
			key='par',
			value=None,
			step=1,
			min_value=1,
			placeholder="Número de parcela",
			help='Identificador de la parcela',
		)

		st.selectbox(
			"Subparcela",
			subplots,
			key='subpar',
			index=None,
			placeholder="Clase de subparcela",
			help='Identificador de la subparcela',
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

		st.selectbox(
			"Forma de crecimiento", 
			growth_forms,
			index=None, 
			key='grow',
			placeholder="Seleccione una forma de crecimiento",
			help='Formas de crcimiento de acuerdo a la documentación del proyecto.'
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
			"CAP",
			key='cap',
			value=None,
			step=0.1,
			placeholder="Circunferencia a la altura de pecho (cm)",
			help='Circunferencia (cm) de los individuos arbóreos o arbustivos a la altura de pecho ---o 1.5 m de altura---.',
		)

		st.number_input(
			"Copa X",
			key='copax',
			value=None,
			step=1,
			placeholder="Diámetro de la copa (cm)",
			help='Diámetro de la copa del individuo a lo largo del eje horizontal de la parcela.',
		)

		st.number_input(
			"Copa Y",
			key='copay',
			value=None,
			step=1,
			placeholder="Diámetro de la copa (cm)",
			help='Diámetro de la copa del individuo a lo largo del eje vertical de la parcela.',
		)

		st.number_input(
			"Cobertura",
			key='cober',
			value=None,
			min_value=1,
			max_value=100,
			step=1,
			placeholder="Cobertura del individuo en la parcela (%)",
			help='Porcentaje del área de la parcela que cubre el individuo. Posibles valores: 1-100%.',
		)

		st.selectbox(
			"Fenología", 
			pheno,
			index=None, 
			key='pheno',
			placeholder="Estado fenológico del individuo",
			help='Posible estado fenológico del individuo.'
		)

		st.number_input(
			"Porcentaje fenología",
			key='per_pheno',
			value=None,
			min_value=1,
			max_value=100,
			step=1,
			placeholder="Estado fenológico del individuo (%).",
			help='Posible estado fenológico del individuo. Posibles valores: 1-100%.'
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
				"Confirmación d información digitada.\n",
				f"Responsable(s): {st.session_state.resp}",
				f"Fecha: {st.session_state.date}",
				f"Hora inicial: {st.session_state.time0}",
				f"Hora final: {st.session_state.timef}",
				f"Sitio: {st.session_state.site}",
				f"Sector: {st.session_state.sector}",
				f"Latitud: {st.session_state.lat}",
				f"Longitud: {st.session_state.lon}",
				f"Parcela: {st.session_state.par}",
				f"Subparcela: {st.session_state.subpar}",
				f"Individuo: {st.session_state.ind}",
				f"Forma de crecimiento: {st.session_state.grow}",
				f"Morfo: {st.session_state.morfo}",
				f"Altura: {st.session_state.alt}",
				#f"CAP: {st.session_state.cap}",
				f"Copa X: {st.session_state.copax}",
				f"Copa Y: {st.session_state.copay}",
				f"Cobertura: {st.session_state.cober}",
				f"Fenología: {st.session_state.pheno}",
				#f"Observaciones individuo: {st.session_state.obs_ind}",
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
			pass

elif len(st.session_state.errors_site) > 0:
	st.session_state.errors_site = "# Error\n\n" + st.session_state.errors_site
	st.info(st.session_state.errors_site)

else: 
	rec_cont.empty()

exit(0)