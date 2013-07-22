//rev 4 adds two direction control

const int forward_motor = 3 ;
const int reverse_motor = 5 ;

const int left_motor = 6 ;
const int right_motor = 9 ;

const double pi = 4 * atan( (float)1 ) ;
const double sigma = 0.3 ;

double phi, phi_r ;
double turning_angle ;
int x_r, y_r ;
int x, y ;
int ro;
int mu = 10;

void test_forward_motion() ;
void test_rotation() ;
void print_coordinates( int x_r, int y_r, int x, int y, double phi ) ;

void get_coordinates( int *x_r, int *y_r, int *x, int *y, double *phi ) ;
double get_reference_angle( int y_r, int x_r, int y, int x ) ;
double get_turning_angle( double phi, double phi_r ) ;
bool within_range( double turning_angle, double sigma ) ;


int get_motor_speed( double turning_angle);
int get_move_speed( double ro);
double get_phi(double phi);

void forward(int motor_speed) ;
void reverse(int motor_speed) ;
void left(int motor_speed) ;
void right(int motor_speed) ;
void stop() ;


void setup() {
	
	Serial.begin( 9600 ) ;

	/* motors */
	pinMode( right_motor, OUTPUT ) ;
	pinMode( left_motor, OUTPUT ) ;
	pinMode( forward_motor, OUTPUT ) ;
	pinMode( reverse_motor, OUTPUT ) ;

	stop();

}

void loop() {
	
	get_coordinates( &x_r, &y_r, &x, &y, &phi ) ;
	phi_r = get_reference_angle( y_r, x_r, y, x ) ;
	turning_angle = get_turning_angle( phi, phi_r ) ;
	ro = sqrt( pow(y_r-y, 2) + pow(x_r - x, 2) );
	if(ro < mu){
		stop();
	}
	else{
		if ( turning_angle > sigma ) {

			if(ro < (2 * mu)){
				digitalWrite(forward_motor, LOW);
				digitalWrite(reverse_motor, LOW);
			}
			if( sin(phi - phi_r) > 0 ){
				right(get_motor_speed(turning_angle));
			}
			if(sin(phi - phi_r) < 0){
				left(get_motor_speed(turning_angle));
			}
			if(cos(phi - phi_r) == -1){
				right(get_motor_speed(turning_angle));
			}
		}
		else{
			digitalWrite(left_motor, LOW);
			digitalWrite(right_motor, LOW);
			ro = sqrt( pow(y_r-y, 2) + pow(x_r - x, 2) );

			if( ro > mu ){
				forward(get_move_speed(ro));
			}
		}
	}	
	delay(10);
}


void get_coordinates( int *x_r, int *y_r, int *x, int *y, double *phi ) {

	if ( Serial.available() > 0 )
		if ( Serial.findUntil( "-", "-" )) {
			*x_r = Serial.parseInt() ;
			*y_r = Serial.parseInt() ;

			*x = Serial.parseInt() ;
			*y = Serial.parseInt() ;
			*phi = (Serial.parseInt() / (float)10000) ;
		}
}

double get_reference_angle( int y_r, int x_r, int y, int x )  {
	double intermediate ; 
	double phi_r ;

	intermediate = atan2( y_r - y, x_r - x ) ;

	// Change -pi to pi range of atan2 to 0 to 2pi of camera coordinates
	if ( (intermediate >= 0) && (intermediate < pi) )
		phi_r = 2 * pi - intermediate ;

	if ( (intermediate > -pi) && (intermediate < 0) )
		phi_r = -intermediate;

	return phi_r ;
}

double get_turning_angle( double phi, double phi_r ) {
	return abs( phi - phi_r ) ;	
}

void forward(int motor_speed) {
	analogWrite( forward_motor, motor_speed ) ;
	digitalWrite( reverse_motor, LOW ) ;
}

void reverse(int motor_speed) {
	digitalWrite( forward_motor, LOW ) ;
	analogWrite( reverse_motor, motor_speed ) ;
}

void left(int motor_speed) {
	analogWrite( left_motor, motor_speed ) ;
	digitalWrite( right_motor, LOW ) ;
}

void right(int motor_speed) {
	analogWrite(right_motor, motor_speed);
	digitalWrite( left_motor, LOW ) ;
}

void stop() {
	digitalWrite( forward_motor, LOW ) ;	
	digitalWrite( reverse_motor, LOW ) ;
	digitalWrite( left_motor, LOW ) ;
	digitalWrite( right_motor, LOW ) ;
}

int get_motor_speed( double turning_angle)
{
	int motor_speed;
	if( turning_angle < 3 * sigma) {
		motor_speed = turning_angle * 35;
	}
	else{
		motor_speed = 254;
	}

	return motor_speed;
}

int get_move_speed( double ro)
{
	int motor_speed;
	if( ro < 1.5 * mu){
		motor_speed =ro / 1.1;
	}
	else{
		motor_speed = 254;
	}

	return motor_speed;
}