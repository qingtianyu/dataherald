import { EMBED_URL } from "@/env-variables";
import { Message } from "@/types/chat";
import { UserProfile, useUser } from "@auth0/nextjs-auth0/client";
import Image from "next/image";
import { FC } from "react";
import { Icon } from "../Layout/Icon";
import ChatAssistantMessageActions from "./ChatAssistantMessageActions";
import { ChatLoader } from "./ChatLoader";
import apiService from "@/services/api";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: FC<ChatMessageProps> = ({ message }) => {
  const { role, content } = message;
  const { user } = useUser();
  const { picture: userPicture } = user as UserProfile;

  const handleThumbsUp = async () => {};

  const handleThumbsDown = async () => {};

  const regularParagraph = (text: string) => (
    <p className="self-center">{text}</p>
  );

  return (
    <div className={`${role === "user" && "bg-gray-100"}`}>
      <div className=" max-w-[1000px] mx-auto">
        <div className="flex flex-col gap-3 p-8">
          <div
            className="flex flex-row items-start gap-3"
            style={{ overflowWrap: "anywhere" }}
          >
            {role === "assistant" ? (
              <Image
                src="/images/dh-logo-symbol-color.svg"
                alt="Dataherald company logo narrow"
                width={40}
                height={40}
                className="pl-1"
              />
            ) : userPicture ? (
              <Image
                src={userPicture}
                alt="User Profile Picture"
                width={35}
                height={35}
                className="rounded-full"
              />
            ) : (
              <Icon
                value="person_outline"
                className="rounded-full bg-gray-200 p-2"
              ></Icon>
            )}
            {typeof content === "string" ? (
              regularParagraph(content)
            ) : content.status === "successful" ? (
              <div className="flex flex-col gap-5 pr-8 overflow-auto">
                <p className="self-center">{content.generated_text}</p>
                {content.viz_id && (
                  <iframe
                    className="min-h-[600px] mb-4 w-full min-w-[300px]"
                    src={`${EMBED_URL}${content.viz_id}?hideDemoLink=true`}
                  ></iframe>
                )}
              </div>
            ) : content.status === "failed" ? (
              <div className="flex flex-col gap-5 pr-8">
                <p className="self-center">{content.generated_text}</p>
                <Image
                  className="mx-auto"
                  src="/images/error/data_not_found.svg"
                  alt="Chat error image"
                  width={600}
                  height={300}
                />
              </div>
            ) : content.status === "loading" ? (
              <div className="flex-1 flex items-center">
                <ChatLoader />
              </div>
            ) : (
              regularParagraph(content.generated_text as string)
            )}
          </div>
          {role === "assistant" &&
            typeof content !== "string" &&
            content.status !== "loading" && (
              <div className="flex flex-row gap-4 self-center">
                <ChatAssistantMessageActions
                  message={content}
                  onThumbsUp={handleThumbsUp}
                  onThumbsDown={handleThumbsDown}
                />
              </div>
            )}
        </div>
      </div>
    </div>
  );
};
