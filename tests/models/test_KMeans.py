import numpy as np
from unittest import TestCase

from diffprivlib.models.k_means import KMeans
from diffprivlib.utils import global_seed, PrivacyLeakWarning, DiffprivlibCompatibilityWarning

global_seed(3141592653)


class TestKMeans(TestCase):
    def test_not_none(self):
        self.assertIsNotNone(KMeans)

    def test_simple(self):
        clf = KMeans(1, [(0, 1)], 3)

        X = np.zeros(1000) + 0.1
        X[:666] = 0.5
        X[:333] = 0.9
        X = X.reshape(-1, 1)

        clf.fit(X)
        centers = clf.cluster_centers_

        self.assertTrue(np.isclose(centers, 0.1, atol=0.05).any())
        self.assertTrue(np.isclose(centers, 0.5, atol=0.05).any())
        self.assertTrue(np.isclose(centers, 0.9, atol=0.05).any())

    def test_unused_args(self):
        with self.assertWarns(DiffprivlibCompatibilityWarning):
            KMeans(verbose=1)

    def test_1d_array(self):
        clf = KMeans()

        X = np.zeros(10)

        with self.assertRaises(ValueError):
            clf.fit(X)

    def test_no_bounds(self):
        clf = KMeans()

        X = np.zeros(10).reshape(-1, 1)

        with self.assertWarns(PrivacyLeakWarning):
            clf.fit(X)

    def test_predict(self):
        clf = KMeans(10, [(0, 1)], 3)

        X = np.array([0.1, 0.1, 0.1, 0.1, 0.5, 0.5, 0.5, 0.5, 0.9, 0.9, 0.9]).reshape(-1, 1)
        clf.fit(X)
        predicted = clf.predict(np.array([0.1, 0.5, 0.9]).reshape(-1, 1))

        # print("Predictions: %s" % str(predicted))
        # print("Centers: %s" % str(clf.cluster_centers_))

        self.assertNotEqual(predicted[0], predicted[1])
        self.assertNotEqual(predicted[0], predicted[2])
        self.assertNotEqual(predicted[2], predicted[1])

    def test_inf_epsilon(self):
        global_seed(3141592653)
        clf = KMeans(float("inf"), [(0, 1)], 3)

        X = np.array([0.1, 0.1, 0.1, 0.1, 0.5, 0.5, 0.5, 0.5, 0.9, 0.9, 0.9]).reshape(-1, 1)
        clf.fit(X)
        centers = clf.cluster_centers_

        self.assertIn(0.1, centers)
        self.assertIn(0.5, centers)
        self.assertIn(0.9, centers)

    def test_many_features(self):
        X = np.random.random(size=(500, 3))
        bounds = [(0, 1)] * 3

        clf = KMeans(bounds=bounds, n_clusters=4)

        clf.fit(X)
        centers = clf.cluster_centers_

        self.assertEqual(centers.shape[0], 4)
        self.assertEqual(centers.shape[1], 3)

        self.assertTrue(np.all(clf.transform(X).argmin(axis=1) == clf.predict(X)))
