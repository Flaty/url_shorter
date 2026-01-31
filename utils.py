from random import randint, choice

def generate_url(start=5, end=10):
        alf = 'QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikolp1234567890'
        length = randint(start, end)
        code = []
        for _ in range(length):
            code.append(choice(alf))
            
        return ''.join(code)
