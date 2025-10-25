from inspect import signature
from dataclasses import dataclass

# https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk
class BaseObject:
    @classmethod
    def from_kwargs(cls, **kwargs):
        # fetch the constructor's signature
        cls_fields = {field for field in signature(cls).parameters}

        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val in kwargs.items():
            if name in cls_fields:
                native_args[name] = val
            else:
                new_args[name] = val

        # use the native ones to create the class ...
        ret = cls(**native_args)

        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

@dataclass
class Stuff(BaseObject):
    main_weapon: str
    secondary_weapon: str
    soda: int
    melees: str
    grenades: str
    medkit: int
    bandage: int
    pills: int
    backpack: str
    chest: str
    helmet: str