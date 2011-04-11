from setuptools import setup

cli_tools = ["spritecss = spritecss.main:main"]

setup(name="spritecss", version="0.5", url="http://yostudios.se/",
      author="Yo Studios AB", author_email="opensource@yostudios.se",
      entry_points={"console_scripts": cli_tools},
      packages=["spritecss", "spritecss.css", "spritecss.packing"])
