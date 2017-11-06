# matrix factorization

import numpy as np
import MPS_localDataSet


# R,P,Q,K
# steps ：the learning rate
# alpha : the regularization parameter
def matrix_factorization(R, P, Q, K, steps=5000, alpha=0.002, beta=0.02):
    Q = Q.T
    for step in range(steps):
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    # eij means the distance
                    eij = R[i][j] - np.dot(P[i, :], Q[:, j])
                    # 根据误差来更新每个维度的值
                    # 此处的梯度是加了正则化项，梯度根据误差公式来求得
                    for k in range(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = np.dot(P, Q)
        # calculate the overall error
        e = 0
        for i in range(len(R)):
            for j in range(len((R[i]))):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - eR[i][j], 2)
                    for k in range(K):
                        e = e + (beta / 2) * (pow(P[i][k], 2) + pow(Q[k][j], 2))
        if e < 0.001:
            break
    return P, Q.T


if __name__ == '__main__':
    path, objPath_extract, objPath_clean,threshold,length = MPS_localDataSet.getPathAndThreshold(20, 1)

    MPS_localDataSet.extractSubDataSet_US(length, path, objPath_extract)
    cleanDataSet = MPS_localDataSet.cleanDataSet(objPath_extract, objPath_clean)
    R = MPS_localDataSet.createCountArray(objPath_clean, 0)

    # R = [
    #     [5, 3, 0, 1],
    #     [4, 0, 0, 1],
    #     [1, 1, 0, 5],
    #     [1, 0, 0, 4],
    #     [0, 1, 5, 4],
    #     ]

    R = np.array(R)
    N = len(R)
    M = len(R[0])
    print(N, M)
    K = 2
    P = np.random.rand(N, K)
    Q = np.random.rand(M, K)
    nP, nQ = matrix_factorization(R, P, Q, K)
    nR = np.dot(nP, nQ.T)
    np.savetxt('Result/R.csv', R, delimiter=',', fmt='%d')
    np.savetxt('Result/nP.csv', nP, delimiter=',', fmt='%.5f')
    np.savetxt('Result/nQ.csv', nQ, delimiter=',', fmt='%.5f')
    np.savetxt('Result/nR.csv', nR, delimiter=',', fmt='%.5f')

    listen_session = MPS_localDataSet.createSequence(objPath_clean, threshold)





    # print(R-nR)
