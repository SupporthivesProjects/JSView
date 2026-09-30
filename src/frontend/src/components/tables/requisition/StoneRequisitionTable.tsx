import useTable from "@lib/hooks/UseTable";
import { useUserState } from "@store/UserState";
import { RequisitionForm } from "./requisitionForm";

export default function StoneRequisitionTable() {
  const table = useTable("stone-requisition");

  const user = useUserState();

  

 

 


  

  return (
    <>
      
      <RequisitionForm />
      
    </>
  );
}
