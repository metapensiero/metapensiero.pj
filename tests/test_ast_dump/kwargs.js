FunctionDef(args=arguments(args=[],
                           defaults=[],
                           kw_defaults=[],
                           kwarg=None,
                           kwonlyargs=[],
                           vararg=None),
            body=[FunctionDef(args=arguments(args=[arg(annotation=None,
                                                       arg='a')],
                                             defaults=[],
                                             kw_defaults=[],
                                             kwarg=arg(annotation=None,
                                                       arg='kwargs'),
                                             kwonlyargs=[],
                                             vararg=None),
                              body=[Pass()],
                              decorator_list=[],
                              name='test',
                              returns=None),
                  Expr(value=Call(args=[Num(n=1)],
                                  func=Name(ctx=Load(),
                                            id='test'),
                                  keywords=[keyword(arg='pippo',
                                                    value=Num(n=2)),
                                            keyword(arg=None,
                                                    value=Name(ctx=Load(),
                                                               id='kwargs'))]))],
            decorator_list=[],
            name='func',
            returns=None)