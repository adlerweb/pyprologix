
from hp3478a import hp3478a
from time import sleep

port = "/dev/ttyACM0"

test = hp3478a(22, port, debug=True)

test.callReset()
test.setDisplay("ADLERWEB.INFO")
print(test.getStatus())
print(test.getDigits(test.status.digits))
print(test.getFunction(test.status.function))
print(test.getRange(test.status.digits))
print(test.setFunction(test.Ω2W))
print(test.setTrigger(test.TRIG_INT))
print(test.setRange("3M"))
print(test.setDigits(3.5))

print(test.getMeasure())

print(test.setRange("A"))
print(test.setDigits(5))

test.getCalibration("calibration.data")
