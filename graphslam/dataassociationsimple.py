import numpy as np
import matplotlib.pyplot as plt
# from tools.conversions import mod_2pi
import gtsam
import gtsam.utils.plot as gtsam_plot

from artelib.homogeneousmatrix import HomogeneousMatrix


class DataAssociationSimple():
    def __init__(self, graphslam, distance_backwards=7, radius_threshold=5.0):
        """
        Given the current estimation in graphSLAM. Do this process:
        a) Extract the current position/orientation x (last current estimate)
        b) Extract a set of candidates C that are , at least, at a distance_backwards distance from the current pose.
        c) Find whether there are candidates in C within a radius_threshold of the current pose.
        d) Obtain a relative transformation to some of the candidates.
        """
        self.graphslam = graphslam
        # look for data associations that are delta_index back in time
        self.distance_backwards = distance_backwards
        self.radius_threshold = radius_threshold
        self.positions = None

    def store_positions(self):
        poses = []
        i = 0
        # fill a vector with all positions
        while self.graphslam.current_estimate.exists(i):
            ce = self.graphslam.current_estimate.atPose3(i)
            T = HomogeneousMatrix(ce.matrix())
            poses.append(T.pos())
            i += 1
        self.positions = np.array(poses)

    def find_candidates(self):
        """
        The function to perform a simple data association.
        The computation of uncertainties is not performed.
        """
        self.store_positions()
        index = self.find_index_backwards()
        candidates = self.find_candidates_within_radius(index)
        return candidates

    # def find_index_backwards(self):
    #     """
    #     Return the maximum index to which we can try to perform data associations.
    #     This is represented by a distance
    #     """
    #     current_pose = self.positions[-1, :]
    #     for i in reversed(range(len(self.positions))):
    #         posei = self.positions[i]
    #         d = np.linalg.norm(current_pose-posei)
    #         if d > self.distance_backwards:
    #             return i
    #     return None

    def find_index_backwards(self):
        """
        Return the maximum index to which we can try to perform data associations.
        This is represented by a distance
        """
        # current_pose = self.positions[-1, :]
        d = 0
        for i in reversed(range(len(self.positions)-1)):
            posei = self.positions[i]
            posei1 = self.positions[i+1]
            di = np.linalg.norm(posei1-posei)
            d += di
            if d > self.distance_backwards:
                return i
        return None


    def find_candidates_within_radius(self, index):
        """
        Find the distance of the current_pose to all the past poses.
        Alternatively: sum the relative distances of consecutive poses.
        """
        if index is None:
            return []
        current_pose = self.positions[-1, :]
        # compute distance to all positions up to index
        positions = self.positions[0:index, :]
        d = np.linalg.norm(positions - current_pose, axis=1)
        print('distances:')
        print(d)
        candidates = np.where(d < self.radius_threshold)[0]
        return candidates
        # for i in range(len(self.positions)-index):
        #     diff = self.positions-current_pose
        #
        #     posei = self.positions[i]
        #     d = np.linalg.norm(current_pose-posei)
        #     if d > self.distance_backwards:
        #         return i


    # def marginal_covariance(self, i):
    #     # init initial estimate, read from self.current_solution
    #     initial_estimate = gtsam.Values()
    #     k = 0
    #     for pose2 in self.graphslam.current_solution:
    #         initial_estimate.insert(k, gtsam.Pose2(pose2[0], pose2[1], pose2[2]))
    #         k = k+1
    #     marginals = gtsam.Marginals(self.graphslam.graph, initial_estimate)
    #     cov = marginals.marginalCovariance(i)
    #     return cov
    #
    # def joint_marginal_covariance(self, i, j):
    #     # init initial estimate, read from self.current_solution
    #     initial_estimate = gtsam.Values()
    #     k = 0
    #     for pose2 in self.graphslam.current_solution:
    #         initial_estimate.insert(k, gtsam.Pose2(pose2[0], pose2[1], pose2[2]))
    #         k = k+1
    #     marginals = gtsam.Marginals(self.graphslam.graph, initial_estimate)
    #     keyvector = gtsam.utilities.createKeyVector([i, j])
    #     jm = marginals.jointMarginalCovariance(variables=keyvector).at(iVariable=i, jVariable=j)
    #     return jm
    #
    # def marginal_information(self, i):
    #     # init initial estimate, read from self.current_solution
    #     initial_estimate = gtsam.Values()
    #     k = 0
    #     for pose2 in self.graphslam.current_solution:
    #         initial_estimate.insert(k, gtsam.Pose2(pose2[0], pose2[1], pose2[2]))
    #         k = k+1
    #     marginals = gtsam.Marginals(self.graphslam.graph, initial_estimate)
    #     cov = marginals.marginalInformation(i)
    #     return cov
    #
    # def joint_marginal_information(self, i, j):
    #     # init initial estimate, read from self.current_solution
    #     initial_estimate = gtsam.Values()
    #     k = 0
    #     for pose2 in self.graphslam.current_solution:
    #         initial_estimate.insert(k, gtsam.Pose2(pose2[0], pose2[1], pose2[2]))
    #         k = k+1
    #     marginals = gtsam.Marginals(self.graphslam.graph, initial_estimate)
    #     keyvector = gtsam.utilities.createKeyVector([i, j])
    #     jm = marginals.jointMarginalInformation(variables=keyvector).at(iVariable=i, jVariable=j)
    #     return jm
    #
    # def joint_mahalanobis(self, i, j, only_position=False):
    #     """
    #     Using an approximation for the joint conditional probability of node i and j
    #     """
    #     Oii = self.marginal_information(i)
    #     Ojj = self.marginal_information(j)
    #     Inf_joint = Oii + Ojj
    #     muii = self.graphslam.current_solution[i]
    #     mujj = self.graphslam.current_solution[j]
    #     mu = mujj-muii
    #     mu[2] = mod_2pi(mu[2])
    #     # do not consider orientation
    #     if only_position:
    #         mu[2] = 0.0
    #     d2 = np.abs(np.dot(mu.T, np.dot(Inf_joint, mu)))
    #     return d2
    #
    # def test_conditional_probabilities(self):
    #     """
    #     """
    #     muii = self.graphslam.current_solution[13]
    #     Sii = self.marginal_covariance(13)
    #
    #     Sjj = self.marginal_covariance(1)
    #     mujj = self.graphslam.current_solution[1]
    #
    #     Sij = self.joint_marginal_covariance(1, 13)
    #     Sji = self.joint_marginal_covariance(13, 1)
    #
    #     Sii_ = Sii - np.dot(Sij, np.dot(np.linalg.inv(Sjj), Sij.T))
    #     Sjj_ = Sjj - np.dot(Sij.T, np.dot(np.linalg.inv(Sii), Sij))
    #
    #
    #     # product, joint probability
    #     Sca = np.linalg.inv(np.linalg.inv(Sii) + np.linalg.inv(Sjj))
    #     Scb = Sii + Sjj
    #     a1 = np.dot(np.linalg.inv(Sii), muii)
    #     a2 = np.dot(np.linalg.inv(Sjj), mujj)
    #     mc = np.dot(Sca, a1+a2)
    #
    #     # gtsam_plot.plot_pose2(0, gtsam.Pose2(muii[0], muii[1], muii[2]), 0.5, Sii)
    #     # gtsam_plot.plot_pose2(0, gtsam.Pose2(mujj[0], mujj[1], mujj[2]), 0.5, Sjj)
    #     # gtsam_plot.plot_pose2(0, gtsam.Pose2(0, 0, 0), 0.5, Sii_)
    #     # gtsam_plot.plot_pose2(0, gtsam.Pose2(0, 1.5, 0), 0.5, Sjj_)
    #     # gtsam_plot.plot_pose2(0, gtsam.Pose2(mc[0], mc[1], mc[2]), 0.5, Sca)
    #
    #     for i in range(10):
    #         mu = 0.5*(mujj + muii)
    #         mu[2] = 0
    #         muij = mujj - muii
    #         muij[2] = 0
    #
    #         gtsam_plot.plot_pose2(0, gtsam.Pose2(muii[0], muii[1], muii[2]), 0.5, Sii)
    #         gtsam_plot.plot_pose2(0, gtsam.Pose2(mujj[0], mujj[1], mujj[2]), 0.5, Sjj)
    #         gtsam_plot.plot_pose2(0, gtsam.Pose2(mu[0], mu[1], mu[2]), 0.5, Sca)
    #         gtsam_plot.plot_pose2(0, gtsam.Pose2(mu[0], mu[1], mu[2]), 0.5, Scb)
    #
    #         d0 = np.dot(muij.T, np.dot(np.linalg.inv(Sca), muij))
    #         d1 = np.dot(muij.T, np.dot(np.linalg.inv(Scb), muij))
    #         # d2 = np.dot(muij.T, np.dot(np.linalg.inv(Sii_), muij))
    #         # d3 = np.dot(muij.T, np.dot(np.linalg.inv(Sjj_), muij))
    #
    #         muii += np.array([0.2, 0, 0])
    #     return True
    #
    # def view_full_information_matrix(self):
    #     """
    #     The function i
    #     """
    #     n = self.graphslam.current_index + 1
    #     H = np.zeros((3*n, 3*n))
    #
    #     for i in range(n):
    #         Hii = self.marginal_information(i)
    #         print(i, i)
    #         print(Hii)
    #         H[3 * i:3 * i + 3, 3 * i:3 * i + 3] = Hii
    #
    #     for i in range(n):
    #         for j in range(n):
    #             if i == j:
    #                 continue
    #             Hij = self.joint_marginal_information(i, j)
    #             print(i, j)
    #             print(Hij)
    #             H[3 * i:3 * i + 3, 3 * j:3 * j + 3] = Hij
    #
    #     plt.figure()
    #     plt.matshow(H)
    #     plt.show()
    #     return True
    #
    # def view_full_covariance_matrix(self):
    #     """
    #     """
    #     n = self.graphslam.current_index + 1
    #     H = np.zeros((3*n, 3*n))
    #
    #     for i in range(n):
    #         Hii = self.marginal_covariance(i)
    #         print(i, i)
    #         print(Hii)
    #         H[3 * i:3 * i + 3, 3 * i:3 * i + 3] = Hii
    #
    #     for i in range(n):
    #         for j in range(n):
    #             if i == j:
    #                 continue
    #             Hij = self.joint_marginal_covariance(i, j)
    #             print(i, j)
    #             print(Hij)
    #             H[3 * i:3 * i + 3, 3 * j:3 * j + 3] = Hij
    #
    #     plt.figure()
    #     plt.matshow(H)
    #     plt.show()
    #     return True

