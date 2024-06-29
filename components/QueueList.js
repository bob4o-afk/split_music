import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

const QueueList = ({ queue }) => {
  return (
    <View style={styles.queueContainer}>
      <FlatList
        data={queue}
        renderItem={({ item }) => <Text>{item.filename} ({item.channel})</Text>}
        keyExtractor={(item, index) => index.toString()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  queueContainer: {
    flex: 1
  }
});

export default QueueList;
