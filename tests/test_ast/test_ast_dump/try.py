## first_stmt_only: True
def func():

    try:
        do_stuff()
    except ValueError:
        fix_value()
    except IndexError as e:
        fix_ix()
    except:
        do()
    finally:
        closeup()
