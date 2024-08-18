import { Avatar } from "./ui/avatar"
import { Card, CardContent, CardHeader } from "./ui/card"

interface CardSectionProps {
    index?: number;
    title?: string;
    children: React.ReactNode;
    className?: string;
}

const CardSection: React.FC<CardSectionProps> = ({ index, title, children, className }) => {
    return (
        <div className={`flex flex-col my-2 ${className}`}>
            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-1">
                        {index && (
                            <Avatar>
                                <span className="sm:text-2xl text-xl ml-2 tracking-tight font-extralight flex items-center">
                                    {index}
                                </span>
                            </Avatar>
                        )}
                        {title && <p className="text-left font-normal sm:text-2xl text-xl">{title}</p>}
                    </div>
                </CardHeader>
                <CardContent>
                    {children}
                </CardContent>
            </Card>
        </div>
    )
}
export default CardSection;