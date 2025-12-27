import ctypes
import time
from typing import Optional, List, Dict, Any
from pylocalmem import Process
from contextlib import contextmanager


class Il2cpp:
    def __init__(self, dll_name: str = "GameAssembly.dll"):
        self.game_asm = ctypes.WinDLL(dll_name)
        self.PROCESS = Process()

        self.il2cpp_domain_get = self.game_asm.il2cpp_domain_get
        self.il2cpp_domain_get.restype = ctypes.c_void_p
        self.il2cpp_domain_get.argtypes = []

        self.il2cpp_thread_attach = self.game_asm.il2cpp_thread_attach
        self.il2cpp_thread_attach.argtypes = [ctypes.c_void_p]
        self.il2cpp_thread_attach.restype = ctypes.c_void_p

        try:
            self.il2cpp_thread_current = self.game_asm.il2cpp_thread_current
            self.il2cpp_thread_current.argtypes = []
            self.il2cpp_thread_current.restype = ctypes.c_void_p
        except AttributeError:
            self.il2cpp_thread_current = None

        try:
            self.il2cpp_thread_detach = self.game_asm.il2cpp_thread_detach
            self.il2cpp_thread_detach.argtypes = [ctypes.c_void_p]
            self.il2cpp_thread_detach.restype = None
        except AttributeError:
            self.il2cpp_thread_detach = None

        self.il2cpp_domain_assembly_open = self.game_asm.il2cpp_domain_assembly_open
        self.il2cpp_domain_assembly_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.il2cpp_domain_assembly_open.restype = ctypes.c_void_p

        self.il2cpp_class_from_name = self.game_asm.il2cpp_class_from_name
        self.il2cpp_class_from_name.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        self.il2cpp_class_from_name.restype = ctypes.c_void_p

        self.il2cpp_class_get_methods = self.game_asm.il2cpp_class_get_methods
        self.il2cpp_class_get_methods.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.il2cpp_class_get_methods.restype = ctypes.c_void_p

        self.il2cpp_class_get_method_from_name = self.game_asm.il2cpp_class_get_method_from_name
        self.il2cpp_class_get_method_from_name.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        self.il2cpp_class_get_method_from_name.restype = ctypes.c_void_p

        self.il2cpp_method_get_name = self.game_asm.il2cpp_method_get_name
        self.il2cpp_method_get_name.argtypes = [ctypes.c_void_p]
        self.il2cpp_method_get_name.restype = ctypes.c_char_p

        self.il2cpp_method_get_param_count = self.game_asm.il2cpp_method_get_param_count
        self.il2cpp_method_get_param_count.argtypes = [ctypes.c_void_p]
        self.il2cpp_method_get_param_count.restype = ctypes.c_int
        
        self.il2cpp_method_get_param = self.game_asm.il2cpp_method_get_param
        self.il2cpp_method_get_param.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.il2cpp_method_get_param.restype = ctypes.c_void_p

        self.il2cpp_runtime_invoke = self.game_asm.il2cpp_runtime_invoke
        self.il2cpp_runtime_invoke.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]
        self.il2cpp_runtime_invoke.restype = ctypes.c_void_p

        self.il2cpp_class_get_fields = self.game_asm.il2cpp_class_get_fields
        self.il2cpp_class_get_fields.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.il2cpp_class_get_fields.restype = ctypes.c_void_p

        self.il2cpp_field_get_name = self.game_asm.il2cpp_field_get_name
        self.il2cpp_field_get_name.argtypes = [ctypes.c_void_p]
        self.il2cpp_field_get_name.restype = ctypes.c_char_p

        self.il2cpp_field_get_type = self.game_asm.il2cpp_field_get_type
        self.il2cpp_field_get_type.argtypes = [ctypes.c_void_p]
        self.il2cpp_field_get_type.restype = ctypes.c_void_p

        self.il2cpp_type_get_name = self.game_asm.il2cpp_type_get_name
        self.il2cpp_type_get_name.argtypes = [ctypes.c_void_p]
        self.il2cpp_type_get_name.restype = ctypes.c_char_p

        self.il2cpp_field_get_offset = self.game_asm.il2cpp_field_get_offset
        self.il2cpp_field_get_offset.argtypes = [ctypes.c_void_p]
        self.il2cpp_field_get_offset.restype = ctypes.c_int

        self.il2cpp_field_get_value = self.game_asm.il2cpp_field_get_value
        self.il2cpp_field_get_value.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

        self.il2cpp_image_get_class = self.game_asm.il2cpp_image_get_class
        self.il2cpp_image_get_class.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.il2cpp_image_get_class.restype = ctypes.c_void_p

        self.il2cpp_image_get_class_count = self.game_asm.il2cpp_image_get_class_count
        self.il2cpp_image_get_class_count.argtypes = [ctypes.c_void_p]
        self.il2cpp_image_get_class_count.restype = ctypes.c_int

        self.il2cpp_class_get_namespace = self.game_asm.il2cpp_class_get_namespace
        self.il2cpp_class_get_namespace.argtypes = [ctypes.c_void_p]
        self.il2cpp_class_get_namespace.restype = ctypes.c_char_p

        self.il2cpp_class_get_name = self.game_asm.il2cpp_class_get_name
        self.il2cpp_class_get_name.argtypes = [ctypes.c_void_p]
        self.il2cpp_class_get_name.restype = ctypes.c_char_p

        self.il2cpp_field_static_get_value = self.game_asm.il2cpp_field_static_get_value
        self.il2cpp_field_static_get_value.restype = None
        self.il2cpp_field_static_get_value.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.il2cpp_field_get_flags = self.game_asm.il2cpp_field_get_flags
        self.il2cpp_field_get_flags.restype = ctypes.c_int
        self.il2cpp_field_get_flags.argtypes = [ctypes.c_void_p]

        self.il2cpp_field_set_value = self.game_asm.il2cpp_field_set_value
        self.il2cpp_field_set_value.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.il2cpp_field_set_value.restype = None

        self.il2cpp_object_unbox = self.game_asm.il2cpp_object_unbox
        self.il2cpp_object_unbox.argtypes = [ctypes.c_void_p]
        self.il2cpp_object_unbox.restype = ctypes.c_void_p

        self.il2cpp_type_get_object = self.game_asm.il2cpp_type_get_object
        self.il2cpp_type_get_object.argtypes = [ctypes.c_void_p]
        self.il2cpp_type_get_object.restype = ctypes.c_void_p

        self.il2cpp_class_get_type = self.game_asm.il2cpp_class_get_type
        self.il2cpp_class_get_type.argtypes = [ctypes.c_void_p]
        self.il2cpp_class_get_type.restype = ctypes.c_void_p

        self.il2cpp_object_get_class = self.game_asm.il2cpp_object_get_class
        self.il2cpp_object_get_class.restype = ctypes.c_void_p
        self.il2cpp_object_get_class.argtypes = [ctypes.c_void_p]

        self.il2cpp_string_new = self.game_asm.il2cpp_string_new
        self.il2cpp_string_new.argtypes = [ctypes.c_char_p]
        self.il2cpp_string_new.restype = ctypes.c_void_p

        self.il2cpp_method_get_return_type = self.game_asm.il2cpp_method_get_return_type
        self.il2cpp_method_get_return_type.argtypes =  [ctypes.c_void_p]
        self.il2cpp_method_get_return_type.restype = ctypes.c_void_p

        self.il2cpp_method_get_flags = self.game_asm.il2cpp_method_get_flags
        self.il2cpp_method_get_flags.argtypes = [ctypes.c_void_p, ctypes.c_int32]
        self.il2cpp_method_get_flags.restype = ctypes.c_int32

        self._domain: Optional[int] = None
        self._attached = False
        self._assembly_cache: Dict[str, int] = {}
        self._image_cache: Dict[int, int] = {}
        self._class_cache: Dict[str, int] = {}

    def _get_domain_raw(self) -> Optional[int]:
        dom = self.il2cpp_domain_get()
        return int(dom) if dom else None

    def ensure_domain_and_attach(self, wait: float = 0.0) -> int:
        """
        Backwards-compatible helper that populates self._domain and performs a single attach.
        This is still used during initialization. Public APIs will attach/detach per-call.
        """
        if self._domain and self._attached:
            return self._domain

        dom = self._get_domain_raw()
        if not dom and wait > 0:
            time.sleep(wait)
            dom = self._get_domain_raw()
        if not dom:
            raise RuntimeError("il2cpp domain not available")

        self._domain = dom
        self.il2cpp_thread_attach(ctypes.c_void_p(dom))
        self._attached = True
        return dom

    @contextmanager
    def _attached_context(self):
        """
        Context manager that re-gets the domain, attaches a thread if the current thread is NOT already
        attached, yields, then detaches (only if we attached).
        This prevents detaching an already-attached (game) thread.
        """
        dom = self._get_domain_raw()
        if not dom:
            raise RuntimeError("il2cpp domain not available")

        
        current_thread = None
        if self.il2cpp_thread_current:
            try:
                current_thread = self.il2cpp_thread_current()
            except Exception:
                current_thread = None

        did_attach = False
        thread_ptr = None

        
        if current_thread:
            try:
                yield
            finally:
                pass
        else:
            
            thread_ptr = self.il2cpp_thread_attach(ctypes.c_void_p(dom))
            did_attach = True
            try:
                yield
            finally:
                if did_attach and self.il2cpp_thread_detach:
                    try:
                        self.il2cpp_thread_detach(thread_ptr)
                    except Exception:
                        
                        pass

    
    def open_assembly(self, assembly_name: str) -> Optional[int]:
        
        with self._attached_context():
            if assembly_name in self._assembly_cache:
                return self._assembly_cache[assembly_name]
            dom = self._get_domain_raw()
            asm = self.il2cpp_domain_assembly_open(ctypes.c_void_p(dom), assembly_name.encode())
            if not asm:
                return None
            self._assembly_cache[assembly_name] = int(asm)
            return int(asm)

    def get_image_from_assembly(self, assembly_ptr: int) -> Optional[int]:
        with self._attached_context():
            if assembly_ptr in self._image_cache:
                return self._image_cache[assembly_ptr]
            try:
                ptr = ctypes.cast(ctypes.c_void_p(assembly_ptr), ctypes.POINTER(ctypes.c_void_p))
                img = int(ptr[0])
            except Exception:
                return None
            self._image_cache[assembly_ptr] = img
            return img

    def get_class_from_name(self, assembly_name: str, namespace: str, klass: str, cache: bool = True) -> Optional[int]:
        key = f"{assembly_name}|{namespace}|{klass}"
        if key in self._class_cache:
            return self._class_cache[key]

        if cache:
            self.list_classes_in_image(assembly_name)
            if key in self._class_cache:
                return self._class_cache[key]

        
        asm = self.open_assembly(assembly_name)
        if not asm:
            return None
        img = self.get_image_from_assembly(asm)
        if not img:
            return None

        with self._attached_context():
            cls = self.il2cpp_class_from_name(ctypes.c_void_p(img), namespace.encode(), klass.encode())
            if not cls:
                return None
            self._class_cache[key] = int(cls)
            return int(cls)

    def find_method(self, assembly_name: str, namespace: str, klass: str, method_name: str, param_count: Optional[int] = None, actualAddress: bool = False, cache: bool = True) -> Optional[int]:
        
        methods = self.list_methods_in_class(assembly_name, namespace, klass, cache=cache)
        if methods:
            for m in methods:
                data = methods[m]
                if m == method_name:
                    ptr = data["method_ptr"]
                    if actualAddress:
                        ptr = self.PROCESS.read_longlong(int(ptr))
                    return int(ptr)

        
        klass_ptr = self.get_class_from_name(assembly_name, namespace, klass, cache=cache)
        if not klass_ptr:
            return None

        param_range = [param_count] if param_count is not None else range(0, 11)
        method_ptr = None

        with self._attached_context():
            for count in param_range:
                method = self.il2cpp_class_get_method_from_name(
                    ctypes.c_void_p(klass_ptr),
                    method_name.encode(),
                    count
                )
                if method:
                    method_ptr = method
                    break

            if not method_ptr:
                return None

            if actualAddress:
                method_ptr = self.PROCESS.read_longlong(int(method_ptr))

        return int(method_ptr)

    def invoke_method(self, method_ptr: int, instance: Optional[int], arg_list: List[Any] = None) -> Optional[int]:
        if not method_ptr:
            raise ValueError("method_ptr is null")

        with self._attached_context():
            argc = len(arg_list) if arg_list else 0
            args = (ctypes.c_void_p * max(1, argc))()
            local_refs = []

            for i, v in enumerate(arg_list or []):

                
                if isinstance(v, (ctypes._SimpleCData, ctypes.Array)):
                    cv = v

                
                elif isinstance(v, bool):
                    cv = ctypes.c_bool(v)

                
                elif isinstance(v, int):
                    cv = ctypes.c_int(v)

                
                elif isinstance(v, float):
                    cv = ctypes.c_float(v)

                
                elif v is None:
                    cv = ctypes.c_void_p(0)

                
                elif isinstance(v, (bytes, bytearray)):
                    cv = (ctypes.c_ubyte * len(v)).from_buffer_copy(v)

                
                elif isinstance(v, str):
                    cv = ctypes.c_void_p(self.il2cpp_string_new(v.encode("utf-8")))

                
                elif isinstance(v, (list, tuple)) and all(isinstance(x, (int, float)) for x in v):
                    ln = len(v)

                    if ln == 2:
                        class Vector2(ctypes.Structure):
                            _fields_ = [
                                ("x", ctypes.c_float),
                                ("y", ctypes.c_float)
                            ]
                        cv = Vector2(*v)

                    elif ln == 3:
                        class Vector3(ctypes.Structure):
                            _fields_ = [
                                ("x", ctypes.c_float),
                                ("y", ctypes.c_float),
                                ("z", ctypes.c_float)
                            ]
                        cv = Vector3(*v)

                    elif ln == 4:
                        class Vector4(ctypes.Structure):
                            _fields_ = [
                                ("x", ctypes.c_float),
                                ("y", ctypes.c_float),
                                ("z", ctypes.c_float),
                                ("w", ctypes.c_float)
                            ]
                        cv = Vector4(*v)

                    else:
                        
                        cv = ctypes.c_void_p(int(v))

                else:
                    cv = ctypes.c_void_p(int(v))

                local_refs.append(cv)
                args[i] = ctypes.cast(ctypes.pointer(cv), ctypes.c_void_p)

            exc = ctypes.c_void_p()
            ret = self.il2cpp_runtime_invoke(
                ctypes.c_void_p(method_ptr),
                ctypes.c_void_p(instance) if instance else None,
                args if argc else None,
                ctypes.byref(exc)
            )

            if not ret:
                return None

            unboxed = self.il2cpp_object_unbox(ret)
            if unboxed:
                return unboxed

            return int(ret)

    def call_method_by_name(self, assembly_name: str, namespace: str, klass: str, method_name: str, instance: Optional[int], param_count: int = None, args: List[Any] = None) -> Optional[int]:
        method = self.find_method(assembly_name, namespace, klass, method_name, param_count)
        if not method:
            return None
        return self.invoke_method(method, instance, args)

    def list_fields_in_class(self, assembly_name: str, namespace: str, klass: str) -> List[Dict[str, Any]]:
        klass_ptr = self.get_class_from_name(assembly_name, namespace, klass)
        if not klass_ptr:
            return []
        fields = {}
        iterator = ctypes.c_void_p()
        with self._attached_context():
            while True:
                field = self.il2cpp_class_get_fields(ctypes.c_void_p(klass_ptr), ctypes.byref(iterator))
                if not field:
                    break
                name_ptr = self.il2cpp_field_get_name(field)
                name = name_ptr.decode() if name_ptr else ""
                type_ptr = self.il2cpp_field_get_type(field)
                type_name = self.il2cpp_type_get_name(type_ptr).decode() if type_ptr else ""
                is_static = (self.il2cpp_field_get_flags(field) & 0x0010) != 0
                fields[name] = {"field_ptr": int(field), "type": type_name, "static": is_static}
        return fields
    
    def list_static_fields_in_class(self, assembly_name: str, namespace: str, klass: str) -> List[Dict[str, Any]]:
        fields = self.list_fields_in_class(assembly_name, namespace, klass)
        static_fields = [field for field in fields if fields[field]['static']]
        return static_fields


    def find_field_in_class(self, assembly_name: str, namespace: str, klass: str, field_name: str) -> Optional[int]:
        fields = self.list_fields_in_class(assembly_name, namespace, klass)
        for field in fields:
            if field == field_name:
                return fields[field]["field_ptr"]
        return None

    def read_field_value(self, assembly_name: str, namespace: str, klass: str, field_name: str, instance: int):
        cls_ptr = self.get_class_from_name(assembly_name, namespace, klass)
        field_ptr = self.find_field_in_class(assembly_name, namespace, klass, field_name)
        if not field_ptr or not instance:
            return None

        with self._attached_context():

            buf = (ctypes.c_byte * 8)()

            self.il2cpp_field_get_value(
                ctypes.c_void_p(instance),
                ctypes.c_void_p(field_ptr),
                ctypes.byref(buf)
            )

            type_ptr = self.il2cpp_field_get_type(ctypes.c_void_p(field_ptr))
            type_name = self.il2cpp_type_get_name(type_ptr).decode() if type_ptr else ""

        raw = ctypes.addressof(buf)

        if "System.Single" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_float))[0]

        if "System.Double" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_double))[0]

        if "System.Int32" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_int))[0]

        if "System.Int64" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_longlong))[0]

        if "System.UInt32" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_uint))[0]

        if "System.UInt64" in type_name:
            return ctypes.cast(raw, ctypes.POINTER(ctypes.c_ulonglong))[0]

        if "System.Boolean" in type_name:
            return bool(ctypes.cast(raw, ctypes.POINTER(ctypes.c_bool))[0])

        return ctypes.cast(raw, ctypes.POINTER(ctypes.c_void_p))[0]
    
    def write_field_value(self, assembly_name: str, namespace: str, klass: str, field_name: str, instance: int, value):
        cls_ptr = self.get_class_from_name(assembly_name, namespace, klass)
        field_ptr = self.find_field_in_class(assembly_name, namespace, klass, field_name)
        if not field_ptr or not instance:
            return False

        
        with self._attached_context():
            type_ptr = self.il2cpp_field_get_type(ctypes.c_void_p(field_ptr))
            type_name = self.il2cpp_type_get_name(type_ptr).decode() if type_ptr else ""

            
            if "System.Single" in type_name:
                cval = ctypes.c_float(value)
            elif "System.Double" in type_name:
                cval = ctypes.c_double(value)
            elif "System.Int32" in type_name:
                cval = ctypes.c_int(value)
            elif "System.Int16" in type_name:
                cval = ctypes.c_short(value)
            elif "System.Int64" in type_name:
                cval = ctypes.c_longlong(value)
            elif "System.Boolean" in type_name:
                cval = ctypes.c_bool(bool(value))
            else:
                
                cval = ctypes.c_void_p(int(value))

            
            self.il2cpp_field_set_value(
                ctypes.c_void_p(instance),
                ctypes.c_void_p(field_ptr),
                ctypes.byref(cval)
            )

        return True

    def read_static_field_value(self, assembly_name: str, namespace: str, klass: str, field_name: str):
        
        field_ptr = self.find_field_in_class(assembly_name, namespace, klass, field_name)
        if not field_ptr:
            return None

        with self._attached_context():
            
            type_ptr = self.il2cpp_field_get_type(ctypes.c_void_p(field_ptr))
            type_name = self.il2cpp_type_get_name(type_ptr).decode() if type_ptr else ""

            if "System.Single" in type_name:
                buf = ctypes.c_float()
            elif "System.Int32" in type_name:
                buf = ctypes.c_int()
            elif "System.Boolean" in type_name:
                buf = ctypes.c_bool()
            else:
                
                buf = ctypes.c_void_p()

            
            self.il2cpp_field_static_get_value(ctypes.c_void_p(field_ptr), ctypes.byref(buf))

        
        if isinstance(buf, ctypes.c_void_p):
            return int(buf.value) if buf.value else None
        else:
            return buf.value

    
    def list_methods_in_class(self, assembly_name: str, namespace: str, klass: str, cache: bool = True) -> List[Dict[str, Any]]:
        key = f"{assembly_name}|{namespace}|{klass}|methods"
        if cache and key in self._class_cache:
            return self._class_cache[key]

        klass_ptr = self.get_class_from_name(assembly_name, namespace, klass, cache=cache)
        if not klass_ptr:
            return []

        methods = {}
        iterator = ctypes.c_void_p()
        with self._attached_context():
            while True:
                method = self.il2cpp_class_get_methods(ctypes.c_void_p(klass_ptr), ctypes.byref(iterator))
                if not method:
                    break
                name_ptr = self.il2cpp_method_get_name(method)
                name = name_ptr.decode() if name_ptr else ""
                param_count = self.il2cpp_method_get_param_count(method)
                param_info = [f"Parameter {i} type: " + self.il2cpp_type_get_name(self.il2cpp_method_get_param(method, i)).decode() for i in range(param_count)]
                return_value = self.il2cpp_type_get_name(self.il2cpp_method_get_return_type(method)).decode()
                is_static = (self.il2cpp_method_get_flags(method, 0) & 0x0010) != 0
                methods[name] = {"method_ptr": int(method), "method_address": self.PROCESS.read_longlong(method), "param_count": param_count, 'param_info': param_info, 'return_value': return_value, 'flags': {'static': is_static}}
        
        if cache:
            self._class_cache[key] = methods

        return methods

    
    def list_classes_in_image(self, assembly_name: str) -> List[str]:
        """
        Enumerate all classes in the given assembly by walking the image's type definitions.
        Returns a list of "namespace.ClassName" strings and caches class pointers.
        """
        asm_ptr = self.open_assembly(assembly_name)
        if not asm_ptr:
            return []

        img_ptr = self.get_image_from_assembly(asm_ptr)
        if not img_ptr:
            return []

        classes = []
        with self._attached_context():
            class_count = self.il2cpp_image_get_class_count(ctypes.c_void_p(img_ptr))
            for i in range(class_count):
                cls_ptr = self.il2cpp_image_get_class(ctypes.c_void_p(img_ptr), i)
                if not cls_ptr:
                    continue
                ns = self.il2cpp_class_get_namespace(ctypes.c_void_p(cls_ptr))
                ns_name = ns.decode() if ns else ""
                cls_name = self.il2cpp_class_get_name(ctypes.c_void_p(cls_ptr))
                cls_name = cls_name.decode() if cls_name else ""
                classes.append(f"{ns_name}.{cls_name}" if ns_name else cls_name)

                
                key = f"{assembly_name}|{ns_name}|{cls_name}"
                self._class_cache[key] = int(cls_ptr)

        return classes


    def list_methods_in_image(self, assembly_name: str) -> Dict[str, Any]:
        classes = self.list_classes_in_image(assembly_name)
        data = {}
        for klass in classes:
            data.setdefault(klass, {})
            methods = self.list_methods_in_class(assembly_name, '', klass)
            for method in methods:
                data[klass][method] = methods[method]

        return data


    def list_static_methods_in_image(self, assembly_name: str) -> Dict[str, Any]:
        classes = self.list_classes_in_image(assembly_name)
        data = {}
        for klass in classes:
            data.setdefault(klass, {})
            methods = self.list_methods_in_class(assembly_name, '', klass)
            for method in methods:
                if methods[method]['flags']['static']:
                    data[klass][method] = methods[method]

        return data

    def list_fields_in_image(self, assembly_name: str) -> Dict[str, Any]:
        classes = self.list_classes_in_image(assembly_name)
        data = {}
        for klass in classes:
            data.setdefault(klass, {})
            fields = self.list_fields_in_class(assembly_name, '', klass)
            for field in fields:
                data[klass][field] = fields[field]

        return data
    

    def list_static_fields_in_image(self, assembly_name: str) -> Dict[str, Any]:
        classes = self.list_classes_in_image(assembly_name)
        data = {}
        for klass in classes:
            data.setdefault(klass, {}).setdefault("fields", [])
            for field in self.list_static_fields_in_class(assembly_name, '', klass):
                data[klass]["fields"].append(field)

        return data