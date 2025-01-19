
from models.conversation import Message, MessageRole

if __name__ == "__main__":
    msg = Message(role=MessageRole.USER, content="Test message")
    print(msg)
    print(msg.to_dict())
    data = msg.to_dict()
    new_msg = Message.from_dict(data)
    print(new_msg)
