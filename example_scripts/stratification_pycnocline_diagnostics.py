"""
stratification_pycnocline_diagnostics.py

Demonstration of pycnocline depth and thickness diagnostics.
The first and second depth moments of stratification are computed as proxies
for pycnocline depth and thickness, suitable for a nearly two-layer fluid.


"""

# %%
import coast
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors  # colormap fiddling

#################################################
# %%  Loading  data
#################################################

#  Loading AMM60 data if it is available
try:
    config = "AMM60"
    dir_AMM60 = "/projectsa/COAsT/NEMO_example_data/AMM60/"
    fil_nam_AMM60 = "AMM60_1d_20100704_20100708_grid_T.nc"
    config_t = "/work/jelt/GitHub/COAsT/config/example_nemo_grid_t.json"
    config_w = "/work/jelt/GitHub/COAsT/config/example_nemo_grid_w.json"
    mon = "July"
    # mon = 'Feb'

    if mon == "July":
        fil_names_AMM60 = "AMM60_1d_201007*_grid_T.nc"
    elif mon == "Feb":
        fil_names_AMM60 = "AMM60_1d_201002*_grid_T.nc"

    chunks = {
        "x_dim": 10,
        "y_dim": 10,
        "t_dim": 10,
    }  # Chunks are prescribed in the config json file, but can be adjusted while the data is lazy loaded.
    sci_t = coast.Gridded(
        fn_data=dir_AMM60 + fil_names_AMM60, fn_domain=dir_AMM60 + "mesh_mask.nc", config=config_t, multiple=True
    )
    sci_t.dataset = sci_t.dataset.chunk(chunks)

    # create an empty w-grid object, to store stratification
    sci_w = coast.Gridded(fn_domain=dir_AMM60 + "mesh_mask.nc", config=config_w)

# OR load in AMM7 example data
except:
    config = "AMM7"
    dn_files = "./example_files/"

    if not os.path.isdir(dn_files):
        print("please go download the examples file from https://linkedsystems.uk/erddap/files/COAsT_example_files/")
        dn_files = input("what is the path to the example files:\n")
        if not os.path.isdir(dn_files):
            print(f"location f{dn_files} cannot be found")

    dn_fig = "unit_testing/figures/"
    fn_nemo_grid_t_dat = "nemo_data_T_grid_Aug2015.nc"
    fn_nemo_dom = "coast_example_nemo_domain.nc"
    config_t = "config/example_nemo_grid_t.json"
    config_w = "config/example_nemo_grid_w.json"

    sci_t = coast.Gridded(dn_files + fn_nemo_grid_t_dat, dn_files + fn_nemo_dom, config=config_t, multiple=True)

    # create an empty w-grid object, to store stratification
    sci_w = coast.Gridded(fn_domain=dn_files + fn_nemo_dom, config=config_w)
print("* Loaded ", config, " data")

#################################################
# %% subset of data and domain ##
#################################################
# Pick out a North Sea subdomain
print("* Extract North Sea subdomain")
ind_sci = sci_t.subset_indices(start=[51, -4], end=[62, 15])
sci_nwes_t = sci_t.isel(y_dim=ind_sci[0], x_dim=ind_sci[1])  # nwes = northwest europe shelf
ind_sci = sci_w.subset_indices(start=[51, -4], end=[62, 15])
sci_nwes_w = sci_w.isel(y_dim=ind_sci[0], x_dim=ind_sci[1])  # nwes = northwest europe shelf

# %% Apply masks to temperature and salinity
if config == "AMM60":
    sci_nwes_t.dataset["temperature_m"] = sci_nwes_t.dataset.temperature.where(
        sci_nwes_t.dataset.mask.expand_dims(dim=sci_nwes_t.dataset["t_dim"].sizes) > 0
    )
    sci_nwes_t.dataset["salinity_m"] = sci_nwes_t.dataset.salinity.where(
        sci_nwes_t.dataset.mask.expand_dims(dim=sci_nwes_t.dataset["t_dim"].sizes) > 0
    )

else:
    # Apply fake masks to temperature and salinity
    sci_nwes_t.dataset["temperature_m"] = sci_nwes_t.dataset.temperature
    sci_nwes_t.dataset["salinity_m"] = sci_nwes_t.dataset.salinity


# %% Construct in-situ density and stratification
print("* Construct in-situ density and stratification")
sci_nwes_t.construct_density(eos="EOS10")

# %% Construct stratification. t-pts --> w-pts
print("* Construct stratification. t-pts --> w-pts")
sci_nwes_w = sci_nwes_t.differentiate(
    "density", dim="z_dim", out_var_str="rho_dz", out_obj=sci_nwes_w
)  # --> sci_nwes_w.rho_dz

#################################################
# %% Create internal tide diagnostics object
print("* Create stratification diagnostics object")
strat = coast.GriddedStratification(sci_nwes_t, sci_nwes_w)

# %%  Construct pycnocline variables: depth and thickness
print("* Compute density and rho_dz if they didn" "t exist")
print("* Compute 1st and 2nd moments of stratification as pycnocline vars")
strat.construct_pycnocline_vars(sci_nwes_t, sci_nwes_w)

# %%  Plot pycnocline variables: depth and thickness
print("* Sample quick plot")
strat.quick_plot()


# %% Make transects
print("* Construct transects to inspect stratification. This is an abuse of the transect code...")
# Example usage: tran = coast.Transect( (54,-15), (56,-12), nemo_f, nemo_t, nemo_u, nemo_v )
tran_it = coast.TransectT(strat, (51, 2.5), (61, 2.5))
tran_w = coast.TransectT(sci_nwes_w, (51, 2.5), (61, 2.5))
tran_t = coast.TransectT(sci_nwes_t, (51, 2.5), (61, 2.5))
print(" - I have forced the w-pt nemo data and w-pt strat data into the t-point Transect objects\n")

lat_sec = tran_t.data.latitude.expand_dims(dim={"z_dim": strat.nz})
dep_sec = tran_t.data.depth_0
tem_sec = tran_t.data.temperature_m.mean(dim="t_dim")

sal_sec = tran_t.data.salinity_m.mean(dim="t_dim")
rho_sec = tran_t.data.density.mean(dim="t_dim")
strat_sec = tran_w.data.rho_dz.mean(dim="t_dim")

zd_sec = tran_it.data.strat_1st_mom.mean(dim="t_dim", skipna=False)
zd_m_sec = tran_it.data.strat_1st_mom_masked.mean(dim="t_dim", skipna=False)

zt_sec = tran_it.data.strat_2nd_mom.mean(dim="t_dim", skipna=False)
zt_m_sec = tran_it.data.strat_2nd_mom_masked.mean(dim="t_dim", skipna=False)


# %% Plot sections
#################
print("* Plot sections with pycnocline depth and thickness overlayed")
plt.pcolormesh(lat_sec, dep_sec, rho_sec)
plt.title("density section")
plt.xlim([51, 62])
plt.ylim([0, 150])
plt.clim([1025, 1028])
plt.gca().invert_yaxis()
plt.colorbar()
plt.show()

plt.pcolormesh(lat_sec, dep_sec, strat_sec)
plt.plot(tran_it.data.latitude, zd_sec, "g", label="unmasked")
plt.plot(tran_it.data.latitude, zd_sec + zt_sec, "g--")
plt.plot(tran_it.data.latitude, zd_sec - zt_sec, "g--")

plt.plot(tran_it.data.latitude, zd_m_sec, "r.", label="masked")
plt.plot(tran_it.data.latitude, zd_m_sec + zt_m_sec, "r.")
plt.plot(tran_it.data.latitude, zd_m_sec - zt_m_sec, "r.")

plt.title("stratification section with pycno vars")
plt.xlim([51, 62])
plt.ylim([0, 150])
plt.clim([-0.2, 0])
plt.gca().invert_yaxis()
plt.colorbar()
plt.legend()
plt.show()


# %% Plot profile of density and stratification with strat_1st_mom in deep water
#############################################################################
print("* Plot profile of density and stratification with strat_1st_mom in deep water")
print(
    " - When the stratification is not nearly two-layer, then then there is no sharp pycnocline for the  1st and 2nd moments to pick out. You end up with a thick \
pycnocline and reduced precision on the depth\n"
)

[JJ, II] = sci_nwes_t.find_j_i(lat=60, lon=2.5)
zd_plus = strat.dataset.strat_1st_mom[0, JJ, II] + strat.dataset.strat_2nd_mom[0, JJ, II]
zd_minus = strat.dataset.strat_1st_mom[0, JJ, II] - strat.dataset.strat_2nd_mom[0, JJ, II]
plt.plot(sci_nwes_w.dataset.rho_dz[0, :, JJ, II], sci_nwes_w.dataset.depth_0[:, JJ, II], "+")
plt.plot(strat.dataset.strat_1st_mom[0, JJ, II], "o", label="strat_1st_mom")
plt.plot(
    [
        0,
        0,
    ],
    [zd_plus, zd_minus],
    "-",
    label="strat_2nd_mom",
)
plt.title("stratification")
plt.ylabel("depth (m)")
plt.gca().invert_yaxis()
plt.legend()
plt.show()

plt.plot(sci_nwes_t.dataset.density[0, :, JJ, II], sci_nwes_t.dataset.depth_0[:, JJ, II], "+")
plt.plot(1027, strat.dataset.strat_1st_mom[0, JJ, II], "o", label="strat_1st_mom")
plt.plot([1027, 1027], [zd_plus, zd_minus], "-", label="strat_2nd_mom")
plt.xlim([1026, 1028])
plt.title("density")
plt.ylabel("depth (m)")
plt.gca().invert_yaxis()
plt.legend()
plt.show()


# %% Map pretty plots of North Sea pycnocline depth
print("* Map pretty plots of North Sea pycnocline depth")
print(" - we expect a RunTimeError here")


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        "trunc({n},{a:.2f},{b:.2f})".format(n=cmap.name, a=minval, b=maxval), cmap(np.linspace(minval, maxval, n))
    )
    return new_cmap


cmap = plt.get_cmap("BrBG_r")
new_cmap = truncate_colormap(cmap, 0.2, 0.8)
# new_cmap.set_bad(color = '#bbbbbb') # light grey
new_cmap.set_under(color="w")  # white.
# It would be nice to plot the unstratified regions different to the land.


H = sci_nwes_t.dataset.depth_0[-1, :, :].squeeze()
lat = sci_nwes_t.dataset.latitude.squeeze()
lon = sci_nwes_t.dataset.longitude.squeeze()

zd = strat.dataset.strat_1st_mom_masked.where(H > 11).mean(dim="t_dim", skipna=True)  # make nan the land
# skipna = True --> ignore masked events when averaging
# skipna = False --> if once masked then mean is masked.

fig = plt.figure(figsize=(8, 9))
# plt.rcParams["figure.figsize"] = (8.0, 12.0)

ax = fig.add_subplot(111)
cz = plt.contour(lon, lat, H, levels=[11, 50, 100, 200], colors=["k", "k", "k", "k"], linewidths=[1, 1, 1, 1])

plt.contourf(lon, lat, zd, levels=np.arange(0, 40.0 + 10.0, 10.0), extend="both", cmap=new_cmap)
ax.set_facecolor("#bbbbbb")  # Set 'underneath' to grey. contourf plots nothing for bad values

plt.xlim([-3, 11])
plt.ylim([51, 62])
plt.colorbar()


lines = [
    cz.collections[i] for i in range(1, len(cz.collections))
]  # [ cz.collections[1], cz.collections[2], cz.collections[-1] ]
labels = [str(int(cz.levels[i])) + "m" for i in range(1, len(cz.levels))]
# labels = ['80m','200m','800m']

# Supress legend
# plt.legend(lines, labels, loc="lower right")

# I expect to see RuntimeWarnings in this block
title_str = (
    strat.dataset["time"].mean(dim="t_dim").dt.strftime("%b %Y: ").values
    + strat.dataset.strat_1st_mom.standard_name
    + " ("
    + strat.dataset.strat_1st_mom.units
    + ")"
)
plt.title(title_str)
plt.xlabel("longitude")
plt.ylabel("latitude")
# plt.show()

fig.savefig("strat_1st_mom.png", dpi=300)
