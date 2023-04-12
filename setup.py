"""
Setup tally package.
"""

if __name__ == '__main__':  # pragma: no cover
    from re import search, M
    from setuptools import setup, find_packages

    def get_version(filename="tally/__init__.py",
                    pattern=r"^__version__ = ['\"]([^'\"]*)['\"]"):
        with open(filename, 'r') as file:
            MATCH = search(pattern, file.read(), M)
            if MATCH:
                return MATCH.group(1)
            else:
                raise RuntimeError("Unable to find version string.")

    def get_description(filename="README.md", linenumber=2):
        with open(filename, 'r') as file:
            return file.readlines()[linenumber].strip()

    VERSION = get_version()
    DESCRIPTION = get_description()

    setup(name='tally',
          version=VERSION,
          package_dir={'tally': 'tally'},
          packages=find_packages(),
          description=DESCRIPTION,
          long_description=open("README.md", "r").read(),
          long_description_content_type="text/markdown",
          url='https://quantumtally.art',
          project_urls={
            'Documentation': 'https://quantumtally.rtfd.io',
            'Source': 'https://github.com/toumix/tally',
            'Tracker': 'https://github.com/toumix/tally/issues',
          },
          keywords='diagrams quantum-computing generative-art',
          author='Alexis Toumi',
          author_email='alexis@toumi.email',
          download_url='https://github.com/toumix/tally/archive/'
                       f'{VERSION}.tar.gz',
          install_requires=[
              l.strip() for l in open('requirements.txt').readlines()],
          python_requires='>=3.9',
          )
