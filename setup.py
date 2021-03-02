import setuptools
from BubotObj.OcfDevice.subtype.DimmerWBMRGBWD import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Bubot_WirenBoard',
    version=__version__,
    author="Razgovorov Mikhail",
    author_email="1338833@gmail.com",
    description="Bubot OCF Driver for IoT modbus devices WirenBoard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/businka/Bubot_WirenBoard",
    package_dir={'': 'src'},
    package_data={
        '': ['*.md', '*.json'],
    },
    packages=setuptools.find_namespace_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
    ],
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        'Bubot_Modbus'
    ]
)
