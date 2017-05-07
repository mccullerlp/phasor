# Declarative Python

Collection of decorators and base classes to allow a declarative style of programming. The 
underlying philosophy can be described as "init considered harmful". Instead, object attributes
are constructed from decorator functions and then stored. The main is essentially like the @property
decorator, but @declarative.mproperty additionally _stores_ (memoizes) the result. 

For classes inheriting declarative.OverridableObject, the @declarative.dproperty attribute can be used
and all properties will be called/accessed within the __init__ constructor to ensure construction. This allows
objects to register with other objects and is convenient for event-loop reactor programming.

The technique of access->construction means that the dependencies between class attributes are resolved
automatically. During the construction of each attribute, any required attributes are accessed and therefore
constructed if they haven't already been.

The price for the convenience is that construction becomes implicit and recursive. The wrappers in this library
do some error checking to aid with this and to properly report AttributeError.

## Quick Example

```python
import declarative

class Child(object):
    id = None

class Parent(object):
    @declarative.mproperty
    def child_registry(self):
        return set()

    @declarative.mproperty
    def c1(self):
        print "Making Parent.c1"
        child = Child()
        child.id = 1
        self.child_registry.add(child)
        return child

    @declarative.mproperty
    def c2(self):
        print "Making Parent.c2"
        child = Child()
        child.id = 1
        self.child_registry.add(child)
        return child

parent = Parent()
parent.c1
#>> Making Parent.c1
parent.c2
#>> Making Parent.c2
print parent.child_registry
```

Ok, so now as the 


## More automatic Example

## Documentation

## Related Documentation
 *  https://fuhm.net/super-harmful/
