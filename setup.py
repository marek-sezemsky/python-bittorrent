try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='python-bittorrent',
    version='0.1',
    description=(
        'python-bittorent is a BitTorrent library, '
        'written entirely in Python'),
    packages=['bittorrent'],
#    zip_safe=True,
)
