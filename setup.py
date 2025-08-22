from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    '''
    This function return list of requirements
    '''
    requirement_lst:List[str]=[]
    try:
        with open ('requirements.txt', 'r')as file:
            #read lines of file
            lines= file.readlines()
            #read each line
            for line in lines:
                requirement=line.strip()
                # ignore empty lines and -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file donot found")

    return requirement_lst

setup(
    name= 'NetworkSecurity',
    version ='0.0.1',
    author ="Aruba",
    email="aruba0397@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)