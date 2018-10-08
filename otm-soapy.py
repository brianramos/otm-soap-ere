import webapp2, simplejson, urllib, random
from pysimplesoap.server import SoapDispatcher, WSGISOAPHandler
from lxml import etree

def getDummyRate(weight):
	weight_number, weight_uom = weight.split(' ')
	cost = float(weight_number) * random.random() * 0.5
	return str(cost)

def cost_shipment(inputDataList):
	return {
			'n:costDetails': {
				'n:costDetail': [{
					'n:cost': getDummyRate(inputDataList.get('inputData')[0].get('values').get('value')),
					'n:currencyCode': 'EUR',
					'n:costType': 'Base'
				}]
			}
		}
	
cost_shipment_service = SoapDispatcher(
	'ExternalRatingService',
	location='http://otm-soapy.appspot.com/cost_shipment',
	action='http://otm-soapy.appspot.com/cost_shipment', #SOAPAction
	namespace='http://xmlns.oracle.com/apps/otm/ExternalRating',
	prefix='n',
	trace=True,
	ns=False,
	response_element='rexRateResult'
	)

cost_shipment_service.register_function('rexRateRequest', cost_shipment,
	returns={
		'n:costDetails': {
			'n:costDetail': [{
				'n:cost': str,
				'n:currencyCode': str,
				'n:costType': str
			}]
		}
	},
	args={
		'inputDataList': {
			'inputData': [{
				'values': {
					'value': str
				}
			}]
		}
	})

def getGmapsDistance(o_lat, o_lon, d_lat, d_lon):
	o_coord = o_lat + ',' + o_lon
	d_coord = d_lat + ',' + d_lon
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&key=AIzaSyD7Ypq1A2P7NWFg3ca8ItPTe61laAq64AU".format(str(o_coord),str(d_coord))
	result= simplejson.load(urllib.urlopen(url))
	return str(result['rows'][0]['elements'][0]['distance']['value'] * 0.001)

def lookup_distance(sourceAddress, destinationAddress, extEngineAuxInputList, edeParam, edeParams):
	
	return {
			'n:uom': 'KM',
			'n:amount': getGmapsDistance(sourceAddress.get('latitude')[0], sourceAddress.get('latitude')[1], destinationAddress.get('latitude')[0], destinationAddress.get('latitude')[1])
			#'n:amount': str(getGmapsDistance(sourceAddress, destinationAddress))
		}

lookup_distance_service = SoapDispatcher(
	'DistanceEngineService',
	location='http://otm-soapy.appspot.com/lookup_distance',
	action='http://otm-soapy.appspot.com/lookup_distance', #SOAPAction
	namespace='http://xmlns.oracle.com/apps/otm/distanceengine',
	prefix='n',
	trace=True,
	ns=True,
	response_element='extEngineDistance'
	)

lookup_distance_service.register_function('lookupDistanceRequest', lookup_distance,
	returns={
		'n:uom': str,
		'n:amount': str
	},
	args={
		'sourceAddress': {
			'countryCode': str,
			'latitude': [str],
			'longitude': str,
			'seqNumber': str
		},
		'destinationAddress': {
			'countryCode': str,
			'latitude': [str],
			'longitude': str,
			'seqNumber': str
		},
		'extEngineAuxInputList': {
			'extEngineAuxInput': [str]
		},
		'edeParam': str,
		'edeParams': str

	})

class CostShipment(webapp2.RequestHandler):
	def get(self):
		self.response.write('''<?xml version='1.0' encoding='UTF-8'?>
<definitions xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
		xmlns:tns="http://xmlns.oracle.com/apps/otm/ExternalRating"
		xmlns:xs="http://www.w3.org/2001/XMLSchema"
		xmlns="http://schemas.xmlsoap.org/wsdl/"
		xmlns:wsam="http://www.w3.org/2007/05/addressing/metadata"
		targetNamespace="http://xmlns.oracle.com/apps/otm/ExternalRating"
		name="ExternalRatingService">
	<types>
		<xs:schema xmlns:tns="http://xmlns.oracle.com/apps/otm/ExternalRating" elementFormDefault="qualified" targetNamespace="http://xmlns.oracle.com/apps/otm/ExternalRating">
			<xs:complexType name="keyValues">
				<xs:annotation>
					<xs:documentation> Name, Values elements
					</xs:documentation>
				</xs:annotation>
				<xs:sequence>
					<xs:element ref="tns:values"/>
				</xs:sequence>
				<xs:attribute name="name" type="xs:string" use="required"/>
			</xs:complexType>
			<xs:simpleType name="costType">
				<xs:annotation>
					<xs:documentation>CostType specifies which kind of cost was calculated.</xs:documentation>
				</xs:annotation>
				<xs:restriction base="xs:string">
					<xs:enumeration value="Base"/>
					<xs:enumeration value="Accessorial"/>
					<xs:enumeration value="Discount"/>
					<xs:enumeration value="SpecialService"/>
				</xs:restriction>
			</xs:simpleType>
			<xs:element name="value" type="xs:string" />
			<xs:element name="inputData" type="tns:keyValues"/>
			<xs:element name="err" type="xs:string" />
			<xs:element name="serviceDays" type="xs:int" nillable='true' />
			<xs:element name="utcPickupDateTime" type="xs:long" />
			<xs:element name="pickupTimezone" type="xs:string" />
			<xs:element name="utcDeliveryDateTime" type="xs:long" />
			<xs:element name="deliveryTimezone" type="xs:string" />
			<xs:element name="chargeableWeight" type="xs:double" nillable='true' />
			<xs:element name="chargeableWeightUom" type="xs:string" />
			<xs:element name="dimWeight" type="xs:double" nillable='true'/>
			<xs:element name="dimWeightUom" type="xs:string" />
			<xs:element name="cost" type="xs:double" nillable='true'/>
			<xs:element name="currencyCode" type="xs:string" />
			<xs:element name="costType" type="tns:costType" />
			<xs:element name="accessorialCode" type="xs:string" />
			<xs:element name="costCode" type="xs:string" />
			<xs:element name="specialServiceCode" type="xs:string" />
			<xs:element name="calculationDetail" type="xs:string"/>
			<xs:element name="isWeightedCostOnly" type="xs:boolean"/>
			<xs:element name="costCategoryGid" type="xs:string" />
			<xs:element name="shipUnitGid" type="xs:string" />
			<xs:element name="shipUnitLineSeq" type="xs:long" />
			<xs:element name="values">
				<xs:complexType>
					<xs:sequence>
						<xs:element ref='tns:value' maxOccurs="unbounded" />
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="calculationDetails">
				<xs:complexType >
					<xs:sequence>
						<xs:element ref="tns:calculationDetail" maxOccurs="unbounded"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="costDetail" >
				<xs:complexType>
					<xs:annotation>
						<xs:documentation>
							This class contains detailed information about an
							individual calculated cost. An invocation of an External Rating Engine can
							return any number of CostDetail records.
							cost:
							Numeric value of the calculated cost.
							currencyCode:
							String representing the currency of the calculated
							cost. Must be a valid currencyCode as understood by OTM. (ex. USD, BGP, etc.)
							costType:
							Type of calculated cost. One of Base, Accessorial,
							Discount, SpecialService.
							accessorialCode:
							If costType is Accessorial, this specifies the
							accessorial code associated with it. Code must be a valid OTM accessorial
							code.
							costCode:
							Alternative code for classification purposes only.
							Applies to all cost types. Code must be a valid OTM accessorial code.
							specialServiceCode:
							If costType is SpecialService, this specifies the
							special service code associated with it. Code must be a valid OTM special
							service code.
							calculationDetails:
							Collection of String containing details about how
							the calculation was performed. There are no restrictions on the generated
							strings, but OTM will only store a maximum of 4000 characters per line.
							isWeightedCostOnly:
							Flag to indicate that the cost should only affect
							the final weighted cost of a shipment If true, the cost will not be added to
							the base or total cost.
							costCategoryGid:
							String specifying a Cost Category Code GID. This
							is a code that allows, within OTM, the ability to specify a set of category
							codes for the purpose of filtering out costs during the rating process. This
							is primarily used for driver assignment during fleet operations. It is
							included here for informational purposes only. This value can be viewed as
							part of the results of an RIQ query.
							sShipUnitGid:
							If the cost should be attached to a particular ship
							unit, the ship unit's ID can be specified here. This is stored on the
							shipment_cost table
							sShipUnitLineSeq:
							If, instead of a ship unit, the cost should be
							associated with a particular ship unit line, this Long can be populated with
							the ship unit line's sequence number. In combination with sShipUnitGid, this
							will complete the primary kew of the s_ship_unit_line table. Again, this is
							stored on the shipment_cost table.
						</xs:documentation>
					</xs:annotation>
					<xs:sequence>
						<xs:element ref="tns:cost"/>
						<xs:element ref="tns:currencyCode" />
						<xs:element ref="tns:costType" />
						<xs:element ref="tns:accessorialCode" />
						<xs:element ref="tns:costCode" />
						<xs:element ref="tns:specialServiceCode" />
						<xs:element ref="tns:calculationDetails" />
						<xs:element ref="tns:isWeightedCostOnly" />
						<xs:element ref="tns:costCategoryGid" />
						<xs:element ref="tns:shipUnitGid" />
						<xs:element ref="tns:shipUnitLineSeq"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="costDetails">
				<xs:complexType>
					<xs:sequence>
						<xs:element ref="tns:costDetail" maxOccurs="unbounded"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="inputDataList">
				<xs:complexType>
					<xs:annotation>
						<xs:documentation>
							InputData Map of RBI ID to List of Strings
							representing the shipment data required
							by the external rating engine. EX:
							{SHIPMENT.NUMLINES,3},
							{SHIPMENT.SOURCE.POSTAL_CODE,19406},
							{SHIPMENT.DEST.POSTAL_CODE,34639},
							{SHIPMENT.RATE.SERVPROV,UPS },
							{SHIPMENT.RATE.RATE_SERVICE,UPS GROUND},
							{SHIPMENT.RATE.SERVPROV_ACCOUNT_NUMBER, 12345634},
							{SHIPMENT.LINES.WEIGHT,{15 LB,10 LB}},
							The RBIs and data present in the map is determined
							by the External Rating Engine Fieldset specified in OTM and associated with the
							calling Rate Offering or Rate Cost/Accessorial Cost.
						</xs:documentation>
					</xs:annotation>
					<xs:sequence>
						<xs:element ref="tns:inputData" maxOccurs="unbounded"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="rexRateRequest">
				<xs:complexType >
					<xs:sequence>
						<xs:element ref="tns:inputDataList"/>
					</xs:sequence>
				</xs:complexType>
			</xs:element>
			<xs:element name="rexRateResult">
				<xs:complexType>
					<xs:annotation>
						<xs:documentation>
							Describes the result of an invocation of an
							External Rating Engine
							err:
							Existence of error message string indicates failure
							The error message will be logged, but will not cause an exception.
							serviceDays:
							If the external rating engine calculates the number
							of service days, it can be returned here. A value of null indicates no data
							utcPickupDateTime:
							If the external rating engine calculates estimated
							pickup and delivery times, they can be returned here.Values of null indicate no
							data. Timezones can be specified if necessary, otherwise, UTC will be assumed.
							pickupTimezone:
							Java-compatible timezone identifier assigned to the
							pickup location (ex. EDT, America/Chicago, etc.)
							utcDeliveryDateTime:
							If the external rating engine calculates estimated
							pickup and delivery times, they can be returned here. Values of null indicate
							no data. Timezones can be specified if necessary, otherwise, UTC will be
							assumed.
							deliveryTimezone:
							Java-compatible timezone identifier assigned to the
							pickup location (ex. EDT, America/Chicago, etc.)
							chargeableWeight:
							Chargeable weight. Copied to the Shipments
							chargeable weight field. Only used when invocation of ERE is specified on the
							Rate Offering
							chargeableWeightUom:
							Unit of Measure for the chargeable weight (ex. LB,
							KG, etc.)
							dimWeight:
							Dimensional weight. Copied to the Shipments
							dimensional weight field. Only used when invocation of ERE is specified on the
							Rate Offering
							dimWeightUom:
							Unit of Measure for the dimensional weight (ex. LB,
							KG, etc.)
						</xs:documentation>
					</xs:annotation>
					<xs:sequence>
						<xs:element ref="tns:err" />
						<xs:element ref="tns:costDetails"/>
						<xs:element ref="tns:serviceDays" />
						<xs:element ref="tns:utcPickupDateTime" />
						<xs:element ref="tns:pickupTimezone" />
						<xs:element ref="tns:utcDeliveryDateTime" />
						<xs:element ref="tns:deliveryTimezone" />
						<xs:element ref="tns:chargeableWeight"/>
						<xs:element ref="tns:chargeableWeightUom" />
						<xs:element ref="tns:dimWeight" />
						<xs:element ref="tns:dimWeightUom" />
					</xs:sequence>
				</xs:complexType>
			</xs:element>
		</xs:schema>
	</types>
	<message name="costShipmentRequest">
		<part name="rexRateRequest" element="tns:rexRateRequest"/>
	</message>
	<message name="costShipmentResponse">
		<part name="rexRateResult" element="tns:rexRateResult"/>
	</message>
	<portType name="ExternalRating">
		<operation name="costShipment">
			<input wsam:Action="http://xmlns.oracle.com/apps/otm/rexExternalService/costShipmentRequest" message="tns:costShipmentRequest"/>
			<output wsam:Action="http://xmlns.oracle.com/apps/otm/rexExternalService/costShipmentResponse" message="tns:costShipmentResponse"/>
		</operation>
	</portType>
	<binding name="ExternalRatingPortBinding" type="tns:ExternalRating">
		<soap:binding transport="http://schemas.xmlsoap.org/soap/http" style="document"/>
		<operation name="costShipment">
			<soap:operation soapAction="costShipment"/>
			<input>
				<soap:body use="literal"/>
			</input>
			<output>
				<soap:body use="literal"/>
			</output>
		</operation>
	</binding>
	<service name="ExternalRatingService">
		<port name="ExternalRatingPort" binding="tns:ExternalRatingPortBinding">
			<soap:address location="https://otm-soapy.appspot.com/cost_shipment"/>
		</port>
	</service>
</definitions>''')

	def post(self):
		soap_request = self.request.body
		soap_response = cost_shipment_service.dispatch(soap_request)
		self.response.content_type = 'text/xml'
		soap_response = soap_response.replace('n:','')
		soap_response = soap_response.replace('xmlns:n="http://xmlns.oracle.com/apps/otm/ExternalRating" ', '')
		self.response.write(soap_response)
	
class LookupDistance(webapp2.RequestHandler):
	def get(self):
		self.response.write('The HTTP Get method is not supported by this URL')

	def post(self):
		soap_request = self.request.body
		soap_response = lookup_distance_service.dispatch(soap_request)
		self.response.content_type = 'text/xml'
		soap_response = soap_response.replace('n:', '')
		soap_response = soap_response.replace('xmlns:n="http://xmlns.oracle.com/apps/otm/distanceengine" ', '')
		self.response.write(soap_response)

app = webapp2.WSGIApplication([
	('/cost_shipment', CostShipment),
	('/lookup_distance', LookupDistance),
	], debug=True)