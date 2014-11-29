try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='twisted-bittorrent',
    version='0.1',
    description=(
        'twisted-bittorent is a Twisted port of python-bittorrent BitTorrent library'),
    packages=['twittorrent'],
    requires=['twisted', 'tornado'],
    zip_safe=True,
)
