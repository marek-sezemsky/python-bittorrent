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
    py_modules=[
        'bencode',
        'bittorrent',
        'simpledb',
        'torrent',
        'tracker',
        'util'],
    zip_safe=True,
)
