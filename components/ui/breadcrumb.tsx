import Link from 'next/link';

export interface BreadcrumbItem {
    label: string;
    href: string;
}

const Breadcrumb: React.FC<{ items: BreadcrumbItem[] }> = ({ items }: { items: BreadcrumbItem[] }) => {

    return (
        <nav className="text-sm font-medium text-gray-500">
            <ol className="flex items-center space-x-2">
                {items.map((item, index) => (
                    <li key={index} className="flex items-center">
                        <span className="mx-2">/</span>
                        <Link href={item.href}>
                            <span className="text-blue-600 hover:text-blue-800">{item.label}</span>
                        </Link>
                    </li>
                ))}
            </ol>
        </nav>
    );
};

export default Breadcrumb;