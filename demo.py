
from hp3478a import hp3478a
from time import sleep

port = "/dev/ttyACM0"

test = hp3478a(22, port, debug=True)

print(test.setDisplay("ADLERWEB.INFO"))
print(test.getMeasure())
print(test.getStatus())
print(test.getDigits(test.status.digits))
print(test.getFunction(test.status.function))
print(test.getRange())
print(test.setAutoZero(0))
sleep(2)
test.setDisplay(None)