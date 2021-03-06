########################
# Author: Naman Tiwari
# Created: 3/19/20
########################

import network
import torch
import os
import numpy as np

np.set_printoptions(precision=6, suppress=True)

def trainNetworks(train_data, train_labels, epochs=5, learning_rate=0.001):
    """
    Trains 6 networks on the data using the hyperparameters provided.
    Saves the final model as in the models directory with timestamp as the name.

    Input is same for all 6 networks. The prediction of each network is for its corresponding
    joint. The labels data structure is divided into

    :param train_data: Numpy array with training data points
    :param val_data: Numpy array with validation data points
    :param steps: Number of training steps
    :param learning_rate: Learning rate used for training
    """

    on_gpu = False
    if torch.cuda.is_available():
        on_gpu = True

    network1 = network.model()
    network2 = network.model()
    network3 = network.model()
    network4 = network.model()
    network5 = network.model()
    network6 = network.model()

    data_length = len(train_data)

    train_data = torch.from_numpy(train_data)
    train_data = train_data.type(torch.FloatTensor)
    train_labels = torch.from_numpy(train_labels)
    train_labels = train_labels.type(torch.FloatTensor)

    if on_gpu:
        network1 = network.model().cuda()
        network2 = network.model().cuda()
        network3 = network.model().cuda()
        network4 = network.model().cuda()
        network5 = network.model().cuda()
        network6 = network.model().cuda()

        #train_data = train_data.cuda()
        #train_labels = train_labels.cuda()

    optimiser1 = torch.optim.Adam(network1.parameters(), learning_rate)
    optimiser2 = torch.optim.Adam(network2.parameters(), learning_rate)
    optimiser3 = torch.optim.Adam(network3.parameters(), learning_rate)
    optimiser4 = torch.optim.Adam(network4.parameters(), learning_rate)
    optimiser5 = torch.optim.Adam(network5.parameters(), learning_rate)
    optimiser6 = torch.optim.Adam(network6.parameters(), learning_rate)

    criterion = torch.nn.MSELoss()

    avg_train_loss = np.empty((0, 6))
    avg_val_loss = np.empty((0, 6))

    print("Starting training!!!")
    # SGD Implementation
    for epoch in range(epochs):
        index = 0

        train_loss = np.empty((0, 6))
        val_loss = np.empty((0, 6))
    
        # Shuffle train_data randomly
        random_perm = np.random.permutation(data_length)
        train_data1 = train_data[random_perm]
        train_labels1 = train_labels[random_perm]

        # Split into train and val
        val_data = train_data1[:int(0.2*data_length),:]
        val_labels = train_labels1[:int(0.2*data_length),:]

        if on_gpu:
            val_data = val_data.cuda()
            val_labels = val_labels.cuda()

        train_data1 = train_data1[int(0.2*data_length):,:]
        train_labels1 = train_labels1[int(0.2*data_length):,:]

        for data, label in zip(train_data1, train_labels1):
            # data = torch.from_numpy(data)
            # data = data.type(torch.FloatTensor)
            # label = torch.from_numpy(label)
            # label = label.type(torch.FloatTensor)
            #print(data)

            if on_gpu:
                data = data.cuda()
                label = label.cuda()

            output1 = network1(data)
            output2 = network2(data)
            output3 = network3(data)
            output4 = network4(data)
            output5 = network5(data)
            output6 = network6(data)

            # Each label frame consists of 6 values corresponding to each joint
            loss1 = criterion(output1, label[0])
            loss2 = criterion(output2, label[1])
            loss3 = criterion(output3, label[2])
            loss4 = criterion(output4, label[3])
            loss5 = criterion(output5, label[4])
            loss6 = criterion(output6, label[5])

            # Backpropagate loss through each network and take gradient step
            optimiser1.zero_grad()
            loss1.backward()
            optimiser1.step()

            optimiser2.zero_grad()
            loss2.backward()
            optimiser2.step()

            optimiser3.zero_grad()
            loss3.backward()
            optimiser3.step()

            optimiser4.zero_grad()
            loss4.backward()
            optimiser4.step()

            optimiser5.zero_grad()
            loss5.backward()
            optimiser5.step()

            optimiser6.zero_grad()
            loss6.backward()
            optimiser6.step()

            with torch.no_grad():
                print("Progress: {}/{}".format(index+1, len(train_data1)), end="\r", flush=True)
                index += 1

                train_loss = np.append(train_loss, np.array([[loss1.item(), loss2.item(), loss3.item(), loss4.item(), loss5.item(), loss6.item()]]), axis=0)

        
        for data, label in zip(val_data, val_labels):
            output1 = network1(data)
            output2 = network2(data)
            output3 = network3(data)
            output4 = network4(data)
            output5 = network5(data)
            output6 = network6(data)

            loss1 = criterion(output1, label[0])
            loss2 = criterion(output2, label[1])
            loss3 = criterion(output3, label[2])
            loss4 = criterion(output4, label[3])
            loss5 = criterion(output5, label[4])
            loss6 = criterion(output6, label[5])
            
            val_loss = np.append(val_loss, np.array([[loss1.item(), loss2.item(), loss3.item(), loss4.item(), loss5.item(), loss6.item()]]), axis=0)
        # Log progress
        print('Epoch: {}'.format(epoch+1))

        mean_train_loss = np.mean(train_loss, axis=0)
        mean_val_loss = np.mean(val_loss, axis=0)

        avg_train_loss = np.append(avg_train_loss, np.array([mean_train_loss]), axis=0)
        avg_val_loss = np.append(avg_val_loss, np.array([mean_val_loss]), axis=0)
        print('Avg Train Loss: \n{}'.format(mean_train_loss))
        print('Avg Val Loss : \n{}\n'.format(mean_val_loss))
                  
    # Save the models after training
    MODELS_DIR = os.path.join('..' + '/models')
    print('Saving models to: {}'.format(MODELS_DIR))

    np.savetxt('../train_results/avg_train_loss.csv', avg_train_loss, fmt='%10.10f', delimiter=',')
    np.savetxt('../train_results/avg_val_loss.csv', avg_val_loss, fmt='%10.10f', delimiter=',')
    
    torch.save(network1.state_dict(), os.path.join(MODELS_DIR, 'network1.torch'))
    torch.save(network2.state_dict(), os.path.join(MODELS_DIR, 'network2.torch'))
    torch.save(network3.state_dict(), os.path.join(MODELS_DIR, 'network3.torch'))
    torch.save(network4.state_dict(), os.path.join(MODELS_DIR, 'network4.torch'))
    torch.save(network5.state_dict(), os.path.join(MODELS_DIR, 'network5.torch'))
    torch.save(network6.state_dict(), os.path.join(MODELS_DIR, 'network6.torch'))
    
            

