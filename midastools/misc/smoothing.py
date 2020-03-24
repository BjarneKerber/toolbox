from med_shape.utils_vtk import vtk_conversion, vtk_mesh
import SimpleITK as sitk
import numpy as np
import argparse
from pathlib import Path


def smooth_img(img,
               smooth_filter='sinc',
               smooth_iter=40,
               relaxation=0.2):
    """
    Smooths input sitk image and return smoothed volume as sitk image.
    Args:
        img: sitk image
        smooth_filter: 'sinc' oder 'laplacian'
        smooth_iter: laplacian smoothing parameters
        relaxation: laplacian smoothing parameters

    Returns: sitk image

    """
    volume = sitk.GetArrayFromImage(img)
    volume = volume.transpose([2, 1, 0])
    vtk_data = vtk_conversion.np_to_vtk_data(volume)
    vtk_image = vtk_conversion.vtk_data_to_image(vtk_data,
                                                 dims=img.GetSize(),
                                                 origin=img.GetOrigin(),
                                                 spacing=img.GetSpacing())

    vtk_poly = vtk_mesh.marching_cube(vtk_image)
    vtk_poly = vtk_mesh.smooth(vtk_poly, smooth_filter='laplacian')

    result = vtk_conversion.poly_to_img(vtk_poly,
                                        origin=img.GetOrigin(),
                                        dim=img.GetSize(),
                                        spacing=img.GetSpacing())

    result = vtk_conversion.vtk_to_numpy_image(result)
    img_result = sitk.GetImageFromArray(result.transpose([2, 1, 0]))
    img_result.SetDirection(img.GetDirection())
    img_result.SetOrigin(img.GetOrigin())
    img_result.SetSpacing(img.GetSpacing())

    return img_result


def main():
    path = '/home/raheppt1/samples_aorta/000_aorta.nii'
    path_out = '/home/raheppt1/samples_aorta/000_aorta_smooth.nii'

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')

    parser.add_argument('-f', '--Filter', help='FilterType',
                        choices={'sinc', 'laplacian'})

    parser.add_argument('--smooth_iter', help='laplacian smoothing iterations', type=int)
    parser.add_argument('--relaxation', help='laplacian smoothing relaxation', type=float)
    args = parser.parse_args()

    nii_file = Path(args.nii_input)

    print(f'Smoothing nii image : {str(nii_file)} ...')
    # todo test if nii file exists
    out_file = args.Output
    if not out_file:
        praefix = 'smooth_'
        if args.Praefix:
            praefix = args.Praefix
        out_file = nii_file.parent.joinpath(praefix + nii_file.name)

    smooth_filter = 'sinc'
    if args.Filter:
        smooth_filter = args.Filter

    smooth_iter = 40
    if args.smooth_iter:
        smooth_iter = args.smooth_iter

    relaxation = 0.2
    if args.relaxation:
        relaxation = args.relaxation

    img = sitk.ReadImage(str(nii_file))
    img_result = smooth_img(img,
               smooth_filter, smooth_iter, relaxation)
    sitk.WriteImage(img_result, str(out_file))

if __name__ == '__main__':
    main()