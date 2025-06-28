import React, { useEffect, useState } from 'react';
import { getAllEmployees, updateEmployee } from '../../api/employees';
import type { Employee } from '../../api/employees';
import '../../App.css';

const AdminEmployeesPage: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedEmployees = await getAllEmployees();
      setEmployees(fetchedEmployees);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Erro desconhecido.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (employee: Employee) => {
    try {
      const updatedEmployee = await updateEmployee(employee.id, {
        is_active: !employee.is_active,
      });
      setEmployees((prevEmployees) =>
        prevEmployees.map((emp) =>
          emp.id === updatedEmployee.id ? updatedEmployee : emp
        )
      );
      alert(
        `Status de ${updatedEmployee.name} atualizado para ${
          updatedEmployee.is_active ? 'Ativo' : 'Inativo'
        }!`
      );
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(`Erro desconhecido ao atualizar ${employee.name}.`);
      }
    }
  };

  if (loading) {
    return <div className="App">Carregando funcionários...</div>;
  }

  if (error) {
    return <div className="App" style={{ color: 'red' }}>Erro: {error}</div>;
  }

  return (
    <div className="App">
      <h1>Gerenciamento de Funcionários</h1>
      <p>Aqui você pode visualizar e gerenciar os funcionários.</p>

      {employees.length === 0 ? (
        <p>Nenhum funcionário encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Ativo</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((employee) => (
              <tr key={employee.id}>
                <td>{employee.id}</td>
                <td>{employee.name}</td>
                <td>{employee.email}</td>
                <td>{employee.is_active ? 'Sim' : 'Não'}</td>
                <td>
                  <button onClick={() => handleToggleActive(employee)}>
                    {employee.is_active ? 'Desativar' : 'Ativar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: '20px' }}>
        <button onClick={fetchEmployees}>Atualizar Lista</button>
        <a href="/admin/dashboard" style={{ marginLeft: '10px' }}>
          Voltar ao Painel Admin
        </a>
      </div>
    </div>
  );
};

export default AdminEmployeesPage;
