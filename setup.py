from setuptools import setup

cli_tools = ["spritemapper = spritecss.main:main"]

setup(name="spritemapper", version="0.5", url="http://yostudios.se/",
      author="Yo Studios AB", author_email="opensource@yostudios.se",
      description="Do-what-I-mean automatic CSS spritemapper",
      license="MIT/X11",
      packages=["spritecss", "spritecss.css", "spritecss.packing"],
      test_suite="nose.collector", tests_require=["nose"],
      entry_points={"console_scripts": cli_tools})
