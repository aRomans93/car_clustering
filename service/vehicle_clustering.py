from PIL import Image
import cv2
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
import json
from glob import glob
from service import utils


class CarGrouper:
    '''
    This class cluster images of cars based on the color of the car 
    using K-Means clustering based on the RGB pixel values.
    '''
    def __init__(self, images_path):
        '''
        Initializes the CarGrouper with the provided parameters.

        Args:
            images_path (str): The id of the compressed folder stored in Google Drive.
        '''
        # Extract and read images from the folder
        self.images_path = utils.extract_images_folder(images_path)
        self.input_images = glob(self.images_path + '/*')
        # Define an input size of images
        self.input_scale = (55, 44)
        # batch size for MiniBatch KMeans
        self.batch_size = min(1024, len(self.input_images))
        # Max number of groups to try for final clustering
        self.max_groups = min(15, len(self.input_images))

    def get_far_grey(self, sorted_colors):
        '''
        Return the centroid with largest distance from Gray RGB value.
        
        Args:
            sorted_colors (numpy.ndarray): an array with two centroids.

        Returns:
            color (numpy.ndarray): chosen centroid.
        '''
        grey_rgb = (128, 128, 128) # Gray RGB point
        color_1 = sorted_colors[0] # first centroid
        color_2 = sorted_colors[1] # second centroid
        # computing euclidian distances
        dist_1 = np.linalg.norm(grey_rgb - color_1)
        dist_2 = np.linalg.norm(grey_rgb - color_2)
        # returning centroid with larges distance
        if dist_1 > dist_2:
            return color_1
        return color_2


    def get_predominant_color(self, i):
        '''
        Compute KMeans in image pixels to obtain the 4 predominant colors found in image.
        
        Args:
            i (int): image index.

        Returns:
            i (int): the index back.
            sorted_colors (numpy.ndarray): The centroid of the predominant colors that is farer from the gray color
        '''
        
        # Read and reshape image
        input_name = self.input_images[i]
        img = cv2.imread(input_name)
        img = cv2.resize(img, self.input_scale, interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # reshape the pixels to 1-d array
        pixels = img.reshape(-1, 3)
        # initialize KMEans and fit with pixels
        kmeans = KMeans(n_clusters=4, n_init=1, max_iter=12)
        labels = kmeans.fit_predict(pixels)
        # Obtain centroid values and sort by number of pixel occurence for each centroid
        centroids = kmeans.cluster_centers_.round(0).astype(int)
        percentages = np.bincount(labels) / len(pixels) * 100
        sorted_indices = np.argsort(percentages)[::-1]
        sorted_colors = centroids[sorted_indices]
        # return row number and the computed data
        return i, self.get_far_grey(sorted_colors[0:2])
    
    def optimal_number_of_clusters(self, wcss):
        '''
        Compute optimal number of clusters for final grouping.
        
        Args:
            wcs (dict): dict containing labels of groups as keys and inertia(score) values as vals.

        Returns:
            k (int): optimal number of groups.
        '''
        x1, y1 = 1, wcss[0]
        x2, y2 = 14, wcss[len(wcss)-1]

        distances = []
        for i in range(len(wcss)):
            x0 = i+2
            y0 = wcss[i]
            numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
            denominator = ((y2 - y1)**2 + (x2 - x1)**2)**(1/2)
            distances.append(numerator/denominator)
        
        return distances.index(max(distances)) + 2


    def group_vehicles(self):
        '''
        Compute optimal number of clusters for final grouping.

        Returns:
            output_json (list): list of groups with name of images.
        '''
        # Create empty array where features for each image will be stored
        main_colors = np.empty([len(self.input_images), 3], dtype=int)
        
        # save predominant color for each image
        for i in range(len(self.input_images)):
            main_colors[i, : ] = self.get_predominant_color(i)[1]

        # compute MiniBatch KMeans of the images for different number of groups
        # Save a dict of scores
        sse = {}
        for i in range(1, self.max_groups): 
            mbk = MiniBatchKMeans(
                n_clusters=i,
                batch_size=self.batch_size,
                n_init=10,
                max_no_improvement=10,
                verbose=0,
            )
            mbk.fit(main_colors)
            sse[i] = mbk.inertia_

        # Obtain optimal number of groups
        optimal_k = self.optimal_number_of_clusters(list(sse.values()))

        # run minibatch Kmeans again for the optimal k
        mbk = MiniBatchKMeans(
            n_clusters=optimal_k,
            batch_size=self.batch_size,
            n_init=10,
            max_no_improvement=10,
            verbose=0,
        )

        # Assigned a predicted color to each image
        labels = mbk.fit_predict(main_colors)
        # obtain RGB values of the groups
        centroids = mbk.cluster_centers_.round(0).astype(int)

        # dict of groups
        groups_dict = {k: [] for k in range(optimal_k)}
        # assign each image to a group, saving the name of the file
        for i, input_name in enumerate(self.input_images):
            input_name = input_name.replace(self.images_path + '/', '')
            groups_dict[labels[i]].append(input_name)

        # Prepare output list
        output_json = []

        # For each predominant color
        for i, color in enumerate(centroids):
            # Get the RGB code
            r, g, b = tuple(color)
            
            # Prepare JSON object
            color_entry = {'color': {'R': f'{r}', 
                                     'G': f'{g}', 
                                     'B': f'{b}'}, 
                           'images': ', '.join(groups_dict[i])}
            
            # Append JSON object to color list
            output_json.append(color_entry)

        # Return the results
        return output_json