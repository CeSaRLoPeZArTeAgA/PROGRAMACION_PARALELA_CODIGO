//PORGAMA DE MANEJO SEMAFORO
const int pin13R=13;//rojo 
const int pin12A=12;//amarillo
const int pin11V=11;//verde
const int t=1000;// para prubeabas usasr t=1000 
float extraVerde = 0.0; // minutos adicionales al verde
float extraRojo  = 0.0; // minutos adicionales al rojo

void setup() {
  Serial.begin(9600);
  pinMode(pin13R,OUTPUT);
  pinMode(pin12A,OUTPUT);
  pinMode(pin11V,OUTPUT);
}

void loop() {
  //prendido de la luz rojo
  leerSerial(); // revisar si llega nueva instrucción
  digitalWrite(pin13R,HIGH);
  // extraRojo está en minutos, entonces multiplicamos por 60 para segundos
  unsigned long tiempoRojo = (60 + extraRojo * 60) * t;
  delay(tiempoRojo);
  //delay(60*t);//tiempo de 1 min
  digitalWrite(pin13R,LOW);//tiempon de 1min + adicional por el paso de la ambulancia(probabilidad)
  delay(500);
  
  //prendido de la luz amarilla
  digitalWrite(pin12A,HIGH);
  delay(15*t);//tiempo de 0.25m
  digitalWrite(pin12A,LOW);
  delay(500);

  //prendido de la luz verde
  leerSerial();
  digitalWrite(pin11V, HIGH);
  // extraVerde está en minutos, lo multiplicamos por 60
  unsigned long tiempoVerde = (180 + extraVerde * 60) * t;
  delay(tiempoVerde);//tiempon de 3min + adicional de la funcion gaussiana
  //delay(180*t);//tiempon de 3min
  digitalWrite(pin11V,LOW);
  delay(500);
}

void leerSerial() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.startsWith("V:")) {
      extraVerde = msg.substring(2).toFloat();
      Serial.print("Nuevo tiempo verde extra: ");
      Serial.println(extraVerde);
    } 
    else if (msg.startsWith("R:")) {
      extraRojo = msg.substring(2).toFloat();
      Serial.print("Nuevo tiempo rojo extra: ");
      Serial.println(extraRojo);
    }
  }
}

