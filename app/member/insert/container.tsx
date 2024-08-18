'use client';

import InsertMemberForm from "./insert-member-form";


// interface ContainerProps { }

export default function Container() {


    return (
        <>
            <InsertMemberForm onSubmit={(data) => { console.log(`data: ${data}`) }} />
        </>
    )
}