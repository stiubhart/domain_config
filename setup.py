import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='domain_config',  
     version='0.1.2',
     scripts=['domain_config'] ,
     author="Stiubhart Deans",
     author_email="stiubhart@btinternet.com",
     description="Quickly configure a domain name .vhost file with an SSL Certificate using Let's Encrypt",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/stiubhart/domain_config",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
