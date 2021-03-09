

def register_kwargs_init( init ):
    def kwarg_init_wrapper( *args, **kwargs ):
        print( args )
        print( kwargs )
        init( *args, **kwargs )

    return kwarg_init_wrapper

def register_kwargs( cls ):
    def kwarg_cls_wrapper( *args, **kwargs ):
        print( args )
        print( kwargs )
        obj = cls( *args, **kwargs )
        return obj

    return kwarg_cls_wrapper
