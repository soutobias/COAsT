[![PyPI version](https://badge.fury.io/py/coast.svg)](https://badge.fury.io/py/coast)
[![Conda COAsT version](https://img.shields.io/conda/v/bodc/coast.svg)](https://anaconda.org/bodc/coast)
[![Anaconda-Server Badge](https://anaconda.org/bodc/coast/badges/latest_release_relative_date.svg)](https://anaconda.org/bodc/coast)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7799863.svg)](https://zenodo.org/record/7799863)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```
__________________________________________________________________________________________


                     ______    ___        _            _________
                   .' ___  | .'   `.     / \          |  _   _  |
                  / .'   \_|/  .-.  \   / _ \     .--.|_/ | | \_|
                  | |       | |   | |  / ___ \   ( (`\]   | |    
                  \ `.___.'\\  `-'  /_/ /   \ \_  `'.'.  _| |_   
                   `.____ .' `.___.'|____| |____|[\__) )|_____|  

                          Coastal Ocean Assessment Toolbox

__________________________________________________________________________________________
```

COAsT is Diagnostic and Assessment toolbox for kilometric scale regional models.
It's aim is to deliver a flexible, community-ready framework for assessing kilometric scale ocean models. The focus, initially, is be on delivering novel diagnostics for processes that are emergent at the kilometric scale and with NEMO model output. The framework leans heavily on xarray.

Documentation can be found [here](https://british-oceanographic-data-centre.github.io/COAsT/docs/).

## Notes on Object Structure and Loading (for contributors):

COAsT is an object-orientated package, meaning that data is stored within Python object
structures. In addition to data storage, these objects contain methods (subroutines)
which allow for manipulation of this data.  An example of such an object is the Gridded
object, which allows for the storage and manipulation of (e.g.) NEMO output and domain data. It
is important to understand how to load data using COAsT and the structure of the resulting
objects.

A Gridded object is created and initialised by passing it the paths of the domain and data
files. Ideally, the grid type should also be specified (T, U, V or F in the case of NEMO).
For example, to load in data from a file containing data on a NEMO T-grid:

```
import coast

fn_data = "<path to T-grid data file(s)>"
fn_domain = "<path to domain file>"
fn_config = "<path to JSON config file>"
data = coast.Gridded(fn_data, fn_domain, fn_config)
```

Ideally, Gridded model output data should be in grid-specific files, i.e.
containing output variables situated on a NEMO T, U, V or F grid, whereas the
grid variables are in a single domain file. On loading into COAsT, only the
grid specific variables appropriate for the paired data are placed into the
Gridded object. A Gridded object therefore contains grid-specific data and all
corresponding grid variables. One of the file names can be omitted (to get a
  data-only or grid only object), however functionality in this case will be
  limited.

Once loaded, data is stored inside the object using an xarray.dataset object.
Following on from the previous code example, this can be viewed by calling:

```
data.dataset
```
This reveals all netcdf-type aspects of the data and domain variables that were loaded,
including dimensions, coordinates, variables and attributes. For example:
```
<xarray.Dataset>
Dimensions:              (axis_nbounds: 2, t_dim: 7, x_dim: 297, y_dim: 375, z_dim: 51)

Coordinates:
    time                 (t_dim) datetime64[ns] 2007-01-01T11:58:56 ... 2007-01-31T11:58:56
    longitude            (y_dim, x_dim) float32 ...
    latitude             (y_dim, x_dim) float32 ...
Dimensions without coordinates: axis_nbounds, t_dim, x_dim, y_dim, z_dim

Data variables:
    deptht_bounds        (z_dim, axis_nbounds) float32 ...
    sossheig             (t_dim, y_dim, x_dim) float32 ...
    time_counter_bounds  (t_dim, axis_nbounds) datetime64[ns] ...
    time_instant         (t_dim) datetime64[ns] ...
    temperature          (t_dim, z_dim, y_dim, x_dim) float32 ...
    e1                   (y_dim, x_dim) float32 ...
    e2                   (y_dim, x_dim) float32 ...
    e3_0                 (z_dim, y_dim, x_dim) float32 1.0 1.0 1.0 ... 1.0 1.0
```
Variables may be obtained in a number of ways. For example, to get temperature data, the
following are all equivalent:
```
temp = data.dataset.temperature
temp = data.dataset['temperature']
temp = data['temperature']
```
These commands will all return an xarray.dataarray object. Manipulation of this object
can be done using xarray commands, for example indexing using [] or xarray.isel. Be aware
that indexing will preserve lazy loading, however and direct access or modifying of the
data will not. For this reason, if you require a subset of the data, it is best to
index first.

The names of common grid variables are standardised within the COAsT package
using JSON configuration files. For example, the following lists COAsT internal
variable followed by the typical NEMO variable names:

1. longitude [glamt / glamu / glamv / glamf]
2. latitude  [gphit / gphiu / gphiv / gphif]
3. time      [time_counter]
4. e1        [e1t / e1u / e1v / e1f] (dx variable)
5. e2        [e1t / e1u / e1v / e1f] (dy variable)
6. e3_0      [e3t_0 / e3u_0 / e3v_0 / e3f_0] (dz variable at time 0)

Longitude, latitude and time are also set as coordinates. You might notice that dimensions
are also standardised:

1. x_dim   The dimension for the x-axis (longitude)
2. y_dim   The dimension for the y-axis (latitude)
3. t_dim   The dimension for the time axis
4. z_dim   The dimension for the depth axis.

Wherever possible, the aim is to ensure that all of the above is consistent across the
whole COAsT toolbox. Therefore, you will also find the same names and dimensions in, for
example observation objects. Future objects, where applicable, will also follow these
conventions. If you (as a contributor) add new objects to the toolbox, following
the above template is strongly encouraged. This includes using xarray dataset/dataarray
objects where possible, adopting an object oriented approach and adhering to naming
conventions.
