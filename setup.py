from setuptools import setup

cli_tools = ["spritecss = spritecss.main:main"]

setup(name="spritecss", version="0.5", url="http://yostudios.se/",
      author="Yo Studios AB", author_email="opensource@yostudios.se",
      packages=["spritecss", "spritecss.css", "spritecss.packing"],
      test_suite="nose.collector", tests_require=["nose"],
      entry_points={"console_scripts": cli_tools})
