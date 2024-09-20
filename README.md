# AbstractionLayerExample
An example application that uses the AbstractionLayer

The `AppCode` folder is your main application that uses the abstraction layer. The abstraction layer is included in directory structure as a submodule. You may want to fork it
so that you can customize the modules and the python build script.

The `AbstractionLayer` is included in the project by a `include` in the `CMakeLists.txt` of your main application.

To compile AbstractionLayer, run `python[3] abstractionLayer.py build`

To run the tests, run `python[3] abstractionLayer.py test`

For a full list of options, run `python[3] abstractionLayer.py help`
