## body_only: True

def func():

    def simple_alert():
        window.alert('Hi there!')

    el = document.querySelector('button')
    el.addEventListener('click', simple_alert)
