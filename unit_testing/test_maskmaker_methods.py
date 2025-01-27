"""

"""

# IMPORT modules. Must have unittest, and probably coast.
import unittest
import coast
import numpy as np
import matplotlib.pyplot as plt
import unit_test_files as files


class test_maskmaker_methods(unittest.TestCase):
    def test_fill_polygon_by_index(self):
        sci = coast.Gridded(files.fn_nemo_dat, files.fn_nemo_dom, config=files.fn_config_t_grid)
        mm = coast.MaskMaker()
        # Draw and fill a square
        vertices_r = [50, 150, 150, 50]
        vertices_c = [50, 50, 150, 150]
        mask00 = np.zeros((sci.dataset.dims["y_dim"], sci.dataset.dims["x_dim"]))
        mask01 = np.ones((sci.dataset.dims["y_dim"], sci.dataset.dims["x_dim"]))
        filled0 = mm.fill_polygon_by_index(mask00, vertices_r, vertices_c)
        filled1 = mm.fill_polygon_by_index(mask01, vertices_r, vertices_c, additive=True)

        # TEST: Check some data
        check1 = filled0[49, 49] == 0 and filled0[51, 51] == 1
        check2 = filled1[49, 49] == 1 and filled1[51, 51] == 2

        self.assertTrue(check1, "check1")
        self.assertTrue(check2, "check2")

    def test_fill_polygon_by_lonlat(self):
        sci = coast.Gridded(files.fn_nemo_dat, files.fn_nemo_dom, config=files.fn_config_t_grid)
        mm = coast.MaskMaker()
        # Draw and fill a square
        vertices_lon = [-5, -5, 5, 5]
        vertices_lat = [40, 60, 60, 40]
        mask00 = np.zeros((sci.dataset.dims["y_dim"], sci.dataset.dims["x_dim"]))
        mask01 = np.ones((sci.dataset.dims["y_dim"], sci.dataset.dims["x_dim"]))
        filled0 = mm.fill_polygon_by_lonlat(
            mask00, sci.dataset.longitude, sci.dataset.latitude, vertices_lon, vertices_lat
        )
        filled1 = mm.fill_polygon_by_lonlat(
            mask01, sci.dataset.longitude, sci.dataset.latitude, vertices_lon, vertices_lat, additive=True
        )

        # TEST: Check some data
        check1 = filled0[50, 50] == 0 and filled0[50, 150] == 1
        check2 = filled1[50, 50] == 1 and filled1[50, 150] == 2

        self.assertTrue(check1, "check1")
        self.assertTrue(check2, "check2")

    def test_make_region_from_vertices(self):
        sci = coast.Gridded(files.fn_nemo_dat, files.fn_nemo_dom, config=files.fn_config_t_grid)
        mm = coast.MaskMaker()
        # Draw and fill a square
        vertices_lon = [-5, -5, 5, 5]
        vertices_lat = [40, 60, 60, 40]
        # input lat/lon as xr.DataArray
        filled1 = mm.make_region_from_vertices(sci.dataset.longitude, sci.dataset.latitude, vertices_lon, vertices_lat)
        # input lat/lon as np.ndarray
        filled2 = mm.make_region_from_vertices(
            sci.dataset.longitude.values, sci.dataset.latitude.values, vertices_lon, vertices_lat
        )

        # TEST: Check some data
        check1 = filled1[50, 50] == 0 and filled1[50, 150] == 1
        check2 = filled2[50, 50] == 0 and filled2[50, 150] == 1

        self.assertTrue(check1, "check1")
        self.assertTrue(check2, "check2")

    def test_make_mask_dataset_and_quick_plot(self):
        sci = coast.Gridded(files.fn_nemo_dat, files.fn_nemo_dom, config=files.fn_config_t_grid)
        mm = coast.MaskMaker()
        # Draw and fill a square
        vertices_lon = [-5, -5, 5, 5]
        vertices_lat = [40, 60, 60, 40]
        # input lat/lon as xr.DataArray
        filled = mm.make_region_from_vertices(sci.dataset.longitude, sci.dataset.latitude, vertices_lon, vertices_lat)

        mask_list = mm.make_mask_dataset(sci.dataset.longitude.values, sci.dataset.latitude.values, filled)

        check = np.isclose(mask_list.mask.values.sum(), 27300)
        self.assertTrue(check, "check")

        with self.subTest("MaskMaker quick plot"):
            mm.quick_plot(mask_list)
            plt.savefig(files.dn_fig + "maskmaker_quick_plot.png")
            plt.close("all")
