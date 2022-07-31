
class A:
	classvar = 10
	def __init__(self, a,b,c):
		self.a=a
		self.b=b
		self.c=c

a=A(1,2,3)
print(str(a.classvar))
a.classvar=9
print(str(a.classvar))

